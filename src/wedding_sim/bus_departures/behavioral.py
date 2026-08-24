"""Behavioral discrete-event model for the end-of-night bus policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from wedding_sim.bus_departures.inputs import BehavioralAssumptions, BusDepartureConstraints, BusSchedule


def _offset(value: str, origin: str) -> float:
    parse = lambda time: datetime.strptime(time, "%H:%M")
    return (parse(value) - parse(origin)).total_seconds() / 60


@dataclass(frozen=True)
class BehavioralResult:
    trials: int
    expected_cost_dollars: float
    expected_bus_two_overtime_minutes: float
    expected_unhappy_guest_minutes: float
    expected_bus_one_riders: float
    coordinator_fill_probability: float
    overflow_probability: float


@dataclass(frozen=True)
class BehavioralRecommendation:
    schedule: BusSchedule
    result: BehavioralResult


def optimize_behavioral_schedule(
    constraints: BusDepartureConstraints,
    assumptions: BehavioralAssumptions = BehavioralAssumptions(),
    *,
    trials: int = 1_000,
    seed: int | None = 42,
) -> BehavioralRecommendation:
    """Grid-search the lowest expected-cost schedule in the allowed ranges."""
    music_end = datetime.strptime(constraints.music_end, "%H:%M")
    earliest = _offset(constraints.first_departure_earliest, constraints.music_end)
    latest = _offset(constraints.first_departure_latest, constraints.music_end)
    candidates = []
    for first_offset in range(int(earliest), int(latest) + 1, 5):
        first_time = (music_end + timedelta(minutes=first_offset)).strftime("%H:%M")
        for gap in range(constraints.bus_gap_minimum_minutes, constraints.bus_gap_maximum_minutes + 1, 5):
            schedule = BusSchedule(first_time, gap)
            result = simulate_behavioral(constraints, schedule, assumptions, trials=trials, seed=seed)
            candidates.append(BehavioralRecommendation(schedule, result))
    # A schedule that leaves more than 55 passengers for Bus 2 is infeasible,
    # regardless of its apparent monetary score.
    return min(
        candidates,
        key=lambda candidate: (
            candidate.result.overflow_probability > 0,
            candidate.result.expected_cost_dollars,
        ),
    )


def simulate_behavioral(constraints: BusDepartureConstraints, schedule: BusSchedule, assumptions: BehavioralAssumptions = BehavioralAssumptions(), *, trials: int = 10_000, seed: int | None = 42) -> BehavioralResult:
    """Simulate equal-weight rider preferences under the 39–55 Bus 1 policy.

    Each rider independently samples an encore outcome, leaving preference, and
    farewell style. This first behavioral version treats a group goodbye as a
    single 15–30 second batch shared by 2–4 riders; individual goodbyes take
    60 seconds. Bus 1 leaves on schedule. Bus 2 holds for all remaining riders.
    """
    if constraints.bus_count != 2 or constraints.bus_capacity != 55:
        raise ValueError("Behavioral model currently requires two 55-seat buses.")
    if constraints.guests_riding > 110 or abs(sum(assumptions.encore_probabilities) - 1) > 1e-9:
        raise ValueError("Riders exceed capacity or encore probabilities do not total 1.")
    rng, b1 = random.Random(seed), _offset(schedule.first_departure, constraints.music_end)
    b2 = b1 + schedule.bus_gap_minutes
    min_b1 = constraints.guests_riding - constraints.bus_capacity
    totals = [0.0] * 6
    ranges = (assumptions.immediate_ready_minutes, assumptions.flexible_ready_minutes, assumptions.linger_ready_minutes)
    for _ in range(trials):
        end = rng.choices(range(5), weights=assumptions.encore_probabilities)[0] * assumptions.song_minutes
        rider_data, server = [], end
        while len(rider_data) < constraints.guests_riding:
            style = rng.randrange(3)  # no goodbye, group, individual
            size = min(rng.choice(assumptions.group_sizes) if style == 1 else 1, constraints.guests_riding - len(rider_data))
            preference, ready = rng.randrange(3), 0.0
            ready = end + rng.uniform(*ranges[preference])
            duration = 0.0 if style == 0 else (rng.uniform(15, 30) if style == 1 else 60) / 60
            complete = ready if style == 0 else max(server, ready) + duration
            server = max(server, complete)
            rider_data.extend({"ready": ready, "complete": complete, "preference": preference} for _ in range(size))
        eligible = sorted((r for r in rider_data if r["complete"] <= b1), key=lambda r: (r["ready"], r["preference"]))[:55]
        if len(eligible) < min_b1:
            totals[4] += 1
            extra = sorted((r for r in rider_data if r not in eligible and r["ready"] <= b1), key=lambda r: (r["preference"], r["ready"]))
            eligible += extra[: min_b1 - len(eligible)]
        bus_one_ids = {id(r) for r in eligible}
        remaining = [r for r in rider_data if id(r) not in bus_one_ids]
        totals[5] += len(remaining) > 55
        actual_b2 = max(b2, max(max(r["ready"], r["complete"]) for r in remaining))
        overtime = actual_b2 - b2
        # Boarding, not departure, ends an immediate leaver's unstructured
        # wait: time spent seated on the bus is explicitly acceptable.
        bus_one_boarding = b1 - constraints.boarding_minutes
        bus_two_boarding = b2 - constraints.boarding_minutes
        unhappy = sum(
            max(
                0.0,
                boarding_opens - rider["ready"] - assumptions.immediate_wait_tolerance_minutes,
            )
            for assigned_riders, boarding_opens in (
                (eligible, bus_one_boarding),
                (remaining, bus_two_boarding),
            )
            for rider in assigned_riders
            if rider["preference"] == 0
        )
        totals[0] += overtime * assumptions.bus_two_overtime_dollars_per_minute + unhappy * assumptions.unhappy_guest_dollars_per_minute
        totals[1] += overtime; totals[2] += unhappy; totals[3] += len(eligible)
    return BehavioralResult(trials, *(value / trials for value in totals))
