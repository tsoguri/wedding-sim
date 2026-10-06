# Wedding Simulation

A Python project exploring the practical details behind a wedding day — how
small delays affect the schedule, how long goodbyes take, and when buses should
leave. The goal is to understand how these details add up and where a little
extra planning can make the day run more smoothly.

## Overview

This project uses Monte Carlo simulation to explore wedding timing and guest
transportation. Each model runs many possible versions of the day, varying
activity lengths and guest behavior to compare outcomes and identify timing
risks. Assumptions are kept explicit alongside the simulation code.

## Simulations

- **Wedding timeline:** Models the day from hair and makeup through the final
  bus departure, tracking how delays carry through connected activities and
  where buffers run thin. The analysis also compares simulated timings with
  recorded actual starts.
- **Bus departures:** Models when guests are ready to leave, time spent saying
  goodbye, and seat capacity. Two-bus schedules are compared to find the lowest
  expected cost based on guest waiting and bus overtime.

The results reflect estimated durations and guest behavior, providing a way to
assess tradeoffs and timing risks. The model notes document these assumptions
and their limitations.

## Analysis and implementation

The analysis lives in two notebooks:

- [Wedding timeline](notebooks/02_wedding_timeline.ipynb) — full-day timing, delay risks, and comparison with actual starts.
- [Bus departures](notebooks/01_bus_departures.ipynb) — guest behavior and departure schedule comparisons.

The Python models live in `src/wedding_sim/`, with assumptions,
simulation logic, and charts grouped by model. The
[timeline notes](src/wedding_sim/timeline/README.md) and
[bus departure notes](src/wedding_sim/bus_departures/README.md) document the
methods, outputs, and limitations.

## Reproducing the analysis

The project uses Python 3.14 and [uv](https://docs.astral.sh/uv/).
The notebooks run with the repository's `.venv` kernel; both models also have
command-line entry points:

```sh
uv sync
uv run wedding-sim timeline
uv run wedding-sim buses --riders 94 --optimize
```
