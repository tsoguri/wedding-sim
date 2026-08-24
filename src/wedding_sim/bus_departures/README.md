# Behavioral model of wedding bus departures

## Abstract

This Monte Carlo discrete-event simulation selects a two-bus departure schedule
for 94 expected riders. It represents uncertain music duration, heterogeneous
guest departure preferences, farewell behavior, Bus 1 capacity, guest waiting,
and Bus 2 overtime. The model minimizes expected dollar cost subject to a
capacity-safe operational policy.

## Decision

`BusDepartureConstraints` holds fixed facts and allowable decision ranges.
`BusSchedule` holds one candidate Bus 1 departure and Bus 2 gap. The optimizer
generates candidate schedules in five-minute increments, so users do not need
to choose an initial departure or gap.

## Probabilistic assumptions

| Quantity | Distribution or value |
| --- | --- |
| Optional songs | 0/1/2/3/4 songs with probabilities 5/10/20/30/35% |
| Song duration | 3 minutes per song |
| Departure preference | Immediate, flexible, or lingerer; equal probability |
| Immediate readiness | Uniformly 0–5 minutes after music ends |
| Flexible readiness | Uniformly 5–20 minutes after music ends |
| Lingerer readiness | Uniformly 15–35 minutes after music ends |
| Farewell style | No goodbye, group goodbye, or individual goodbye; equal probability |
| Group farewell | 2–4 riders; one uniformly 15–30 second interaction |
| Individual farewell | One 60-second interaction |

These are deliberately transparent priors, not measurements of this guest
list. Edit `BehavioralAssumptions` in `inputs.py` as better information becomes
available.

## Operational policy

- One combined couple goodbye line serves one farewell batch at a time.
- Each bus has 55 seats; 94 riders require Bus 1 to take at least 39 riders.
- Bus 1 never leaves early and departs at its stated time with 39–55 riders.
  A coordinator fills it to 39 from ready guests if necessary.
- Groups may split across buses.
- Riders left for Bus 2 may board from 15 minutes before its stated departure.
- Bus 2 waits for all remaining riders; it is the only bus that may depart late.

## Cost function

Each trial costs:

```text
$5 × Bus 2 minutes after its stated departure
$1.5 × immediate-leaver minutes beyond a five-minute tolerance before their assigned bus opens for boarding
```

Any candidate with a nonzero probability of leaving more than 55 riders for Bus
2 is rejected as infeasible before cost comparison.

## Outputs and limitations

The model reports expected cost, Bus 2 overtime, unhappy guest-minutes, Bus 1
occupancy, coordinator-fill probability, and capacity-overflow probability.
It does not model bus arrival delays, actual rider survey data, parking/staging,
or parallel farewell lines. Results are decision support, not a guarantee.

## Reproduction

```sh
uv run wedding-sim buses --riders 94
uv run wedding-sim buses --riders 94 --optimize
```
