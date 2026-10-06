"""Recorded wedding-day start times and their comparison with the simulation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from wedding_sim.timeline.simulation import TimelineResult, clock_to_minutes


@dataclass(frozen=True)
class ActualStart:
    """One observed start time, keyed to a timeline event."""

    event_key: str
    actual_start: str
    phase: str
    note: str = ""


@dataclass(frozen=True)
class EventComparison:
    """Observed start versus planned and simulated starts, in minutes after midnight."""

    key: str
    label: str
    phase: str
    planned_start_minutes: float
    p50_start_minutes: float
    p90_start_minutes: float
    actual_start_minutes: float
    note: str = ""

    @property
    def delay_vs_plan_minutes(self) -> float:
        return self.actual_start_minutes - self.planned_start_minutes

    @property
    def minutes_past_p90(self) -> float:
        return self.actual_start_minutes - self.p90_start_minutes

    @property
    def beyond_p90(self) -> bool:
        return self.minutes_past_p90 > 0.5


def load_actual_starts(path: str | Path | None = None) -> tuple[ActualStart, ...]:
    """Read observed start times; defaults to the bundled ``data/actual_starts.csv``."""
    source = Path(path) if path is not None else files("wedding_sim.timeline").joinpath("data/actual_starts.csv")
    with source.open(newline="") as handle:
        return tuple(
            ActualStart(row["event_key"], row["actual_start"], row["phase"], row.get("note") or "")
            for row in csv.DictReader(handle)
        )


def compare_to_actuals(result: TimelineResult, actuals: tuple[ActualStart, ...] | None = None) -> tuple[EventComparison, ...]:
    """Pair each observed start with its event's planned, P50, and P90 simulated start."""
    actuals = actuals if actuals is not None else load_actual_starts()
    comparisons = []
    for actual in actuals:
        event = result.event(actual.event_key)
        comparisons.append(EventComparison(
            key=event.key,
            label=event.label,
            phase=actual.phase,
            planned_start_minutes=event.planned_start_minutes,
            p50_start_minutes=event.p50_start_minutes,
            p90_start_minutes=event.p90_start_minutes,
            actual_start_minutes=clock_to_minutes(actual.actual_start),
            note=actual.note,
        ))
    return tuple(comparisons)
