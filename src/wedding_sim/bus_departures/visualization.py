"""Matplotlib charts for the behavioral bus-departure model."""

from wedding_sim.bus_departures.behavioral import BehavioralRecommendation, BehavioralResult
from wedding_sim.bus_departures.inputs import BusDepartureConstraints


def _minutes_from_music(time: str, music_end: str) -> float:
    from datetime import datetime

    parse = lambda value: datetime.strptime(value, "%H:%M")
    return (parse(time) - parse(music_end)).total_seconds() / 60


def _clock_after_music(minutes: float, music_end: str) -> str:
    from datetime import datetime, timedelta

    clock = datetime.strptime(music_end, "%H:%M") + timedelta(minutes=minutes)
    return clock.strftime("%-I:%M %p")


def plot_recommendation(
    constraints: BusDepartureConstraints,
    recommendation: BehavioralRecommendation,
    result: BehavioralResult | None = None,
    ax=None,
):
    """Plot the recommended timing, optionally using a final simulation result."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4.5))
    metrics = result or recommendation.result
    first = _minutes_from_music(recommendation.schedule.first_departure, constraints.music_end)
    second = first + recommendation.schedule.bus_gap_minutes
    actual_second = second + metrics.expected_bus_two_overtime_minutes

    for row, departure, label in ((1, first, "Bus 1"), (0, second, "Bus 2")):
        ax.barh(
            row, constraints.boarding_minutes, left=departure - constraints.boarding_minutes,
            height=0.4, color="#6b8e23", label="Boarding window" if row == 1 else None, zorder=2,
        )
        ax.axvline(departure, color="#333333", linestyle="--", linewidth=1, zorder=1)
        ax.annotate(
            f"{label} departs {_clock_after_music(departure, constraints.music_end)}",
            xy=(departure, row), xytext=(6, 20), textcoords="offset points",
            fontsize=9, fontweight="bold", ha="left", va="bottom", clip_on=False,
        )

    if actual_second > second:
        ax.barh(
            0, actual_second - second, left=second, height=0.4,
            color="#c97775", label="Expected Bus 2 overtime", zorder=2,
        )
        ax.annotate(
            f"+{metrics.expected_bus_two_overtime_minutes:.0f} min expected overtime",
            xy=(actual_second, 0), xytext=(-8, 0), textcoords="offset points",
            fontsize=8.5, ha="right", va="center", color="#7a2e2e",
        )

    ax.axvline(0, color="#333333", linewidth=1.5, label="Scheduled music end", zorder=1)
    ax.set_yticks([0, 1], ["Bus 2", "Bus 1"])
    ax.set_ylim(-0.7, 1.9)
    ax.set_xlabel("Minutes after scheduled music end")
    ax.set_title(f"Recommended schedule — expected cost ${metrics.expected_cost_dollars:.0f}", pad=14)
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False, fontsize=9)
    return ax


def plot_behavioral_summary(result: BehavioralResult, ax=None):
    """Show the expected cost components of one behavioral scenario."""
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))
    overtime_cost = result.expected_bus_two_overtime_minutes * 5
    wait_cost = result.expected_unhappy_guest_minutes
    ax.bar(["Bus 2 overtime", "Guest wait"], [overtime_cost, wait_cost], color=["#c97775", "#6b8e23"])
    ax.set_ylabel("Expected dollars per simulated wedding")
    ax.set_title(f"Expected total cost: ${result.expected_cost_dollars:.0f}")
    return ax
