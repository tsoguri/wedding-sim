"""Command-line access to the included simulations."""

from __future__ import annotations

import argparse

from wedding_sim.bus_departures import (
    BusDepartureConstraints,
    BusSchedule,
    optimize_behavioral_schedule,
    simulate_behavioral,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run wedding logistics simulations.")
    subcommands = parser.add_subparsers(dest="simulation", required=True)
    buses = subcommands.add_parser("buses", help="Model bus departures and farewells.")
    buses.add_argument("--riders", type=int, default=85)
    buses.add_argument("--capacity", type=int, default=55)
    buses.add_argument("--music-end", default="22:00", help="24-hour time, e.g. 22:00")
    buses.add_argument("--first-departure", help="Evaluate this 24-hour Bus 1 departure.")
    buses.add_argument("--bus-gap", type=int, help="Evaluate this Bus 2 gap in minutes.")
    buses.add_argument("--seed", type=int, default=42, help="Random seed for reproducible trials.")
    buses.add_argument("--optimize", action="store_true", help="Find the lowest-cost behavioral schedule.")
    args = parser.parse_args()
    if args.simulation == "buses":
        constraints = BusDepartureConstraints(args.riders, args.capacity, 2, args.music_end)
        if args.optimize:
            print(optimize_behavioral_schedule(constraints, seed=args.seed))
        elif args.first_departure is not None and args.bus_gap is not None:
            print(simulate_behavioral(constraints, BusSchedule(args.first_departure, args.bus_gap), seed=args.seed))
        else:
            parser.error("provide --optimize or both --first-departure and --bus-gap")
