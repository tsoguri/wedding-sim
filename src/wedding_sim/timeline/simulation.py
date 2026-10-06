"""Monte Carlo delay propagation for the wedding-day timeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from wedding_sim.timeline.inputs import TimelineEvent, default_timeline


def clock_to_minutes(value: str) -> float:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def minutes_to_clock(value: float) -> str:
    base = datetime(2000, 1, 1) + timedelta(minutes=value)
    return base.strftime("%-I:%M %p")


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    fraction = position - lower
    if fraction == 0:
        return ordered[lower]
    return ordered[lower] + fraction * (ordered[lower + 1] - ordered[lower])


@dataclass(frozen=True)
class EventSummary:
    key: str
    label: str
    category: str
    planned_start_minutes: float
    planned_end_minutes: float
    expected_start_minutes: float
    expected_end_minutes: float
    p50_start_minutes: float
    p90_start_minutes: float
    p90_end_minutes: float
    expected_delay_minutes: float
    start_late_probability: float
    over_10_minutes_late_probability: float


@dataclass(frozen=True)
class TimelineResult:
    trials: int
    events: tuple[EventSummary, ...]
    ceremony_on_time_probability: float
    ceremony_over_10_minutes_late_probability: float
    dessert_before_bus_boarding_probability: float
    expected_program_buffer_before_bus_minutes: float
    p10_program_buffer_before_bus_minutes: float

    def event(self, key: str) -> EventSummary:
        """Look up one event summary by key."""
        try:
            return next(event for event in self.events if event.key == key)
        except StopIteration as error:
            raise KeyError(key) from error


def _validate_and_plan(events: tuple[TimelineEvent, ...]) -> tuple[dict[str, float], dict[str, float]]:
    if not events:
        raise ValueError("timeline must contain at least one event")
    starts: dict[str, float] = {}
    ends: dict[str, float] = {}
    for event in events:
        if event.key in starts:
            raise ValueError(f"duplicate timeline event key: {event.key}")
        triggers = []
        for dependency in event.dependencies:
            if dependency.event not in starts:
                raise ValueError(f"{event.key} depends on missing or later event {dependency.event}")
            reference = starts if dependency.point == "start" else ends
            triggers.append(reference[dependency.event] + dependency.lag_minutes)
        if event.scheduled_start is None and not triggers:
            raise ValueError(f"{event.key} needs a scheduled start or dependency")
        # The plan is the supplied clock time; only untimed events derive theirs from dependencies.
        starts[event.key] = clock_to_minutes(event.scheduled_start) if event.scheduled_start else max(triggers)
        ends[event.key] = starts[event.key] + event.duration.most_likely
    return starts, ends


def simulate_timeline(
    events: tuple[TimelineEvent, ...] | None = None,
    *,
    trials: int = 10_000,
    seed: int | None = 42,
) -> TimelineResult:
    """Run independent triangular duration draws through the dependency graph."""
    if trials <= 0:
        raise ValueError("trials must be positive")
    events = events or default_timeline()
    planned_starts, planned_ends = _validate_and_plan(events)
    rng = random.Random(seed)
    trial_starts = {event.key: [] for event in events}
    trial_ends = {event.key: [] for event in events}

    for _ in range(trials):
        starts: dict[str, float] = {}
        ends: dict[str, float] = {}
        for event in events:
            triggers = []
            for dependency in event.dependencies:
                reference = starts if dependency.point == "start" else ends
                triggers.append(reference[dependency.event] + dependency.lag_minutes)
            earliest = clock_to_minutes(event.scheduled_start) if event.scheduled_start else float("-inf")
            start = max([earliest, *triggers])
            estimate = event.duration
            duration = rng.triangular(estimate.minimum, estimate.maximum, estimate.most_likely)
            starts[event.key] = start
            ends[event.key] = start + duration
            trial_starts[event.key].append(start)
            trial_ends[event.key].append(start + duration)

    summaries = []
    for event in events:
        starts = trial_starts[event.key]
        ends = trial_ends[event.key]
        planned = planned_starts[event.key]
        delays = [start - planned for start in starts]
        summaries.append(EventSummary(
            key=event.key,
            label=event.label,
            category=event.category,
            planned_start_minutes=planned,
            planned_end_minutes=planned_ends[event.key],
            expected_start_minutes=sum(starts) / trials,
            expected_end_minutes=sum(ends) / trials,
            p50_start_minutes=_percentile(starts, 0.50),
            p90_start_minutes=_percentile(starts, 0.90),
            p90_end_minutes=_percentile(ends, 0.90),
            expected_delay_minutes=sum(delays) / trials,
            start_late_probability=sum(delay > 1e-9 for delay in delays) / trials,
            over_10_minutes_late_probability=sum(delay > 10 for delay in delays) / trials,
        ))

    required = {"ceremony", "dessert", "bus_1_boarding"}
    missing = required - trial_starts.keys()
    if missing:
        raise ValueError(f"timeline is missing required reporting events: {', '.join(sorted(missing))}")
    ceremony_delays = [start - planned_starts["ceremony"] for start in trial_starts["ceremony"]]
    buffers = [
        boarding - dessert
        for boarding, dessert in zip(trial_starts["bus_1_boarding"], trial_ends["dessert"], strict=True)
    ]
    return TimelineResult(
        trials=trials,
        events=tuple(summaries),
        ceremony_on_time_probability=sum(delay <= 1e-9 for delay in ceremony_delays) / trials,
        ceremony_over_10_minutes_late_probability=sum(delay > 10 for delay in ceremony_delays) / trials,
        dessert_before_bus_boarding_probability=sum(buffer >= 0 for buffer in buffers) / trials,
        expected_program_buffer_before_bus_minutes=sum(buffers) / trials,
        p10_program_buffer_before_bus_minutes=_percentile(buffers, 0.10),
    )


def format_timeline_result(result: TimelineResult) -> str:
    """Format the headline risks and selected event percentiles for the CLI."""
    lines = [
        f"Wedding timeline Monte Carlo ({result.trials:,} trials)",
        f"Ceremony starts on time: {result.ceremony_on_time_probability:.1%}",
        f"Ceremony starts >10 min late: {result.ceremony_over_10_minutes_late_probability:.1%}",
        f"Dessert served before Bus 1 boarding: {result.dessert_before_bus_boarding_probability:.1%}",
        f"Expected buffer before Bus 1 boarding: {result.expected_program_buffer_before_bus_minutes:.1f} min",
        f"10th-percentile buffer before Bus 1 boarding: {result.p10_program_buffer_before_bus_minutes:.1f} min",
        "",
        "Selected event starts (planned / median / 90th percentile):",
    ]
    for key in ("first_look", "ceremony", "entrance_couple", "main_course", "dessert"):
        event = result.event(key)
        lines.append(
            f"  {event.label}: {minutes_to_clock(event.planned_start_minutes)} / "
            f"{minutes_to_clock(event.p50_start_minutes)} / {minutes_to_clock(event.p90_start_minutes)}"
        )
    return "\n".join(lines)
