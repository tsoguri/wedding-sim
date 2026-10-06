# Monte Carlo wedding-day timeline

## Abstract

This simulation propagates uncertain activity durations through the current
wedding-day schedule. It preserves clock-time anchors, supports parallel
activities, and delays an activity only when one of its prerequisites finishes
late. It estimates where buffers are thin rather than predicting one exact day.

## Current schedule

`default_timeline()` in `inputs.py` contains the supplied schedule from the
8:45 AM hair-and-makeup setup through the 10:45 PM Bus 2 departure. Activities
with supplied times keep those times as their earliest possible starts.
Activities without supplied times derive their planned starts from dependencies
and most-likely durations.

The reception's most-likely sequence is:

```text
Taiko → guest seating → entrances → first dance → dance set
      → Hamotzi/first course → parent dances → Hora → dance set
      → main course → cake → couple toast → bouquet → dance set → dessert
```

Toasts begin 15 minutes into their associated course and therefore overlap the
meal. Cocktail hour and yichud run in parallel. Bus times are fixed milestones,
not activities delayed by the reception program.

## Probabilistic assumptions

Every non-milestone activity has a transparent triangular duration estimate:
minimum, most likely, and maximum. For example, the ceremony is modeled as
27/30/40 minutes and the Hora as 8/12/18 minutes. The mode generally matches
the current schedule; the wider upper bound represents ordinary wedding-day
slippage. Exact estimates are defined alongside the schedule in `inputs.py` so
they can be replaced with planner or vendor estimates.

Each trial independently samples every activity duration. An event starts at
the later of:

1. its stated clock time, when one exists; and
2. all dependency triggers, which can reference another event's start or end.

This is a precedence-network Monte Carlo model. It does not impose a global
delay on unrelated events: a late photography session can delay the Ketubah and
ceremony, while guest arrival still begins at 4:00 PM.

## Outputs

The result reports, for every activity:

- planned, expected, median, and 90th-percentile timing;
- probability of any start delay;
- probability of starting more than ten minutes late.

Headline measures report ceremony punctuality and how much reception-program
buffer remains before Bus 1 boarding at 10:15 PM. `plot_timeline` visualizes
planned durations and finish uncertainty; `plot_delay_risk` ranks accumulated
delay risk.

## Comparing with the actual day

`data/actual_starts.csv` records observed start times (24-hour clock) keyed by
event. `compare_to_actuals(result)` pairs each with its planned, P50, and P90
simulated start, and `comparison_html(comparisons)` in `visualization.py`
renders a static HTML/SVG strip chart for the notebook. "Planned" is the clock
time supplied in `inputs.py`; untimed events derive theirs from those clock
times and most-likely durations.

## Important interpretation

The defaults are informed placeholders, not measured vendor performance.
Duration samples are independent, which omits shared causes such as weather or
a generally fast/slow coordinator. The model does not yet simulate room travel,
vendor resource contention beyond explicit dependencies, meal-service capacity,
or a decision to shorten later dance sets after a delay. A high risk is a prompt
to confirm estimates and add an operational recovery rule, not a guarantee that
the event will run late.

## Reproduction

```sh
uv run wedding-sim timeline
uv run wedding-sim timeline --trials 50000 --seed 7
```
