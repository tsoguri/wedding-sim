"""Schedule and probabilistic assumptions for the wedding-day timeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DurationEstimate:
    """A triangular duration estimate, expressed in minutes."""

    minimum: float
    most_likely: float
    maximum: float

    def __post_init__(self) -> None:
        if not 0 <= self.minimum <= self.most_likely <= self.maximum:
            raise ValueError("duration estimates must satisfy 0 <= minimum <= most_likely <= maximum")


@dataclass(frozen=True)
class EventDependency:
    """Start after another event's start or end, plus an optional lag."""

    event: str
    point: str = "end"
    lag_minutes: float = 0.0

    def __post_init__(self) -> None:
        if self.point not in {"start", "end"}:
            raise ValueError("dependency point must be 'start' or 'end'")


@dataclass(frozen=True)
class TimelineEvent:
    """One activity or milestone in the timeline dependency graph."""

    key: str
    label: str
    duration: DurationEstimate
    scheduled_start: str | None = None
    dependencies: tuple[EventDependency, ...] = ()
    category: str = "Reception"


def fixed(minutes: float) -> DurationEstimate:
    """Return a deterministic duration estimate."""
    return DurationEstimate(minutes, minutes, minutes)


def default_timeline() -> tuple[TimelineEvent, ...]:
    """Return the current wedding schedule with editable duration priors.

    Fixed clock times come from the supplied timeline. For activities without a
    clock time, the planned start is derived from their dependencies and the
    most-likely duration of preceding activities.
    """
    d = DurationEstimate
    dep = EventDependency
    return (
        TimelineEvent("beauty_setup", "Hair and makeup setup", d(10, 15, 25), "08:45", category="Getting ready"),
        TimelineEvent("k_makeup", "K makeup", d(42, 50, 65), "09:00", (dep("beauty_setup"),), "Getting ready"),
        TimelineEvent("s_hair", "S hair", d(42, 50, 65), "09:00", (dep("beauty_setup"),), "Getting ready"),
        TimelineEvent("s_makeup", "S makeup", d(42, 50, 65), "09:50", (dep("k_makeup"), dep("s_hair")), "Getting ready"),
        TimelineEvent("k_hair", "K hair", d(42, 50, 65), "10:00", (dep("s_hair"), dep("k_makeup")), "Getting ready"),
        TimelineEvent("a_grooming", "A grooming", d(10, 20, 30), "10:50", (dep("s_makeup"),), category="Getting ready"),
        TimelineEvent("s2_makeup", "S2 makeup", d(42, 50, 65), "11:20", (dep("a_grooming"),), "Getting ready"),
        TimelineEvent("j_hair", "J hair", d(42, 50, 65), "11:20", (dep("k_hair"),), "Getting ready"),
        TimelineEvent("getting_ready_portraits", "Getting-ready portraits", d(35, 50, 60), "12:00", (dep("a_grooming"),), "Photography"),
        TimelineEvent("j_makeup", "J makeup", d(42, 50, 65), "12:10", (dep("s2_makeup"),), "Getting ready"),
        TimelineEvent("s2_hair", "S2 hair", d(42, 50, 65), "12:10", (dep("j_hair"),), "Getting ready"),
        TimelineEvent(
            "first_look", "First-look portraits", d(25, 30, 40), "13:00",
            (dep("getting_ready_portraits"), dep("j_makeup"), dep("s2_hair")), "Photography",
        ),
        TimelineEvent("immediate_family", "Couple and immediate-family portraits", d(50, 60, 75), "13:30", (dep("first_look"),), "Photography"),
        TimelineEvent("extended_family", "Extended-family and wedding-party photos", d(60, 75, 90), "14:30", (dep("immediate_family"),), "Photography"),
        TimelineEvent("ketubah", "Ketubah signing and Bedeken", d(25, 30, 40), "15:45", (dep("extended_family"),), "Ceremony"),
        TimelineEvent("guest_arrival", "Guest arrival", d(15, 30, 40), "16:00", category="Guests"),
        TimelineEvent("processional_lineup", "Processional lineup", d(8, 10, 15), "16:20", (dep("ketubah"),), "Ceremony"),
        TimelineEvent("ceremony", "Wedding ceremony", d(27, 30, 40), "16:30", (dep("processional_lineup"),), "Ceremony"),
        TimelineEvent("cocktail_hour", "Cocktail hour", d(55, 65, 75), "17:00", (dep("ceremony"),), "Reception"),
        TimelineEvent("yichud", "Yichud", d(12, 15, 20), "17:00", (dep("ceremony"),), "Ceremony"),
        TimelineEvent("join_cocktail", "Couple joins cocktail hour", fixed(0), "17:20", (dep("yichud"),), "Reception"),
        TimelineEvent("taiko", "Taiko performance", d(8, 10, 12), "17:55", (dep("cocktail_hour"),), "Reception"),
        TimelineEvent("entrance_lineup", "Grand-entrance lineup", d(5, 8, 12), "18:00", (dep("cocktail_hour"),), "Reception"),
        TimelineEvent("entrance_bride_parents", "Grand entrance: bride's parents", d(0.5, 1, 2), dependencies=(dep("taiko"), dep("entrance_lineup")), category="Reception"),
        TimelineEvent("entrance_groom_parents", "Grand entrance: groom's parents", d(0.5, 1, 2), dependencies=(dep("entrance_bride_parents"),), category="Reception"),
        TimelineEvent("entrance_wedding_party", "Grand entrance: wedding party", d(2, 3, 5), dependencies=(dep("entrance_groom_parents"),), category="Reception"),
        TimelineEvent("entrance_couple", "Grand entrance: wedding couple", d(1, 2, 3), dependencies=(dep("entrance_wedding_party"),), category="Reception"),
        TimelineEvent("first_dance", "First dance", d(3, 4, 6), dependencies=(dep("entrance_couple"),), category="Dancing"),
        TimelineEvent("dance_set_1", "Dance set 1", d(15, 20, 30), dependencies=(dep("first_dance"),), category="Dancing"),
        TimelineEvent("hamotzi", "Hamotzi blessing", d(2, 3, 5), dependencies=(dep("dance_set_1"),), category="Meal"),
        TimelineEvent("first_course", "First course", d(28, 35, 45), dependencies=(dep("hamotzi"), ), category="Meal"),
        TimelineEvent("best_man_toast", "Best Man toast", d(3, 5, 8), dependencies=(dep("first_course", "start", 15),), category="Toasts"),
        TimelineEvent("maid_of_honor_toast", "Maid of Honor toast", d(3, 5, 8), dependencies=(dep("best_man_toast"),), category="Toasts"),
        TimelineEvent(
            "mother_son_dance", "Mother-son dance", d(3, 4, 6),
            dependencies=(dep("first_course"), dep("maid_of_honor_toast")), category="Dancing",
        ),
        TimelineEvent("father_daughter_dance", "Father-daughter dance", d(3, 4, 6), dependencies=(dep("mother_son_dance"),), category="Dancing"),
        TimelineEvent("hora", "Hora", d(8, 12, 18), dependencies=(dep("father_daughter_dance"),), category="Dancing"),
        TimelineEvent("dance_set_2", "Dance set 2", d(15, 20, 30), dependencies=(dep("hora"),), category="Dancing"),
        TimelineEvent("main_course", "Main course", d(35, 40, 50), dependencies=(dep("dance_set_2"),), category="Meal"),
        TimelineEvent("dad_1_toast", "Dad 1's toast", d(3, 5, 8), dependencies=(dep("main_course", "start", 15),), category="Toasts"),
        TimelineEvent("dad_2_toast", "Dad 2's toast", d(3, 5, 8), dependencies=(dep("dad_1_toast"),), category="Toasts"),
        TimelineEvent("cake_cutting", "Cake cutting", d(4, 5, 8), dependencies=(dep("main_course"), dep("dad_2_toast")), category="Reception"),
        TimelineEvent("couple_toast", "Couple's toast", d(3, 4, 7), dependencies=(dep("cake_cutting"),), category="Toasts"),
        TimelineEvent("bouquet_presentation", "Bride's bouquet presentation", d(3, 4, 7), dependencies=(dep("couple_toast"),), category="Reception"),
        TimelineEvent("dance_set_3", "Dance set 3", d(35, 45, 60), dependencies=(dep("bouquet_presentation"),), category="Dancing"),
        TimelineEvent("dessert", "Dessert served", fixed(0), dependencies=(dep("dance_set_3"),), category="Meal"),
        TimelineEvent("bus_1_boarding", "Guests board Bus 1", fixed(0), "22:15", category="Transportation"),
        TimelineEvent("bus_1_departure", "Bus 1 departs", fixed(0), "22:30", category="Transportation"),
        TimelineEvent("bus_2_boarding", "Guests board Bus 2", fixed(0), "22:30", category="Transportation"),
        TimelineEvent("bus_2_departure", "Bus 2 departs", fixed(0), "22:45", category="Transportation"),
    )
