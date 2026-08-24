"""Assumptions for the bus-departure simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BusDepartureConstraints:
    """Fixed facts and allowable schedule ranges for the bus decision."""

    guests_riding: int = 85
    bus_capacity: int = 55
    bus_count: int = 2
    music_end: str = "22:00"
    boarding_minutes: int = 15
    first_departure_earliest: str = "22:00"
    first_departure_latest: str = "23:00"
    bus_gap_minimum_minutes: int = 0
    bus_gap_maximum_minutes: int = 60


@dataclass(frozen=True)
class BusSchedule:
    """One proposed pair of stated departures to evaluate."""

    first_departure: str
    bus_gap_minutes: int


@dataclass(frozen=True)
class BehavioralAssumptions:
    """Equal-weight guest-choice priors used when survey data is unavailable."""

    encore_probabilities: tuple[float, ...] = (0.05, 0.10, 0.20, 0.30, 0.35)
    song_minutes: float = 3.0
    immediate_ready_minutes: tuple[float, float] = (0.0, 5.0)
    flexible_ready_minutes: tuple[float, float] = (5.0, 20.0)
    linger_ready_minutes: tuple[float, float] = (15.0, 35.0)
    immediate_wait_tolerance_minutes: float = 5.0
    group_sizes: tuple[int, ...] = (2, 3, 4)
    bus_two_overtime_dollars_per_minute: float = 5.0
    unhappy_guest_dollars_per_minute: float = 1.5
