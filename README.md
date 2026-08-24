# wedding-sim

Reusable, transparent simulations for wedding-day logistics and guest
experience. Each simulation keeps its assumptions, calculation, visualization,
and technical notes together so scenarios can be adjusted and compared in a
notebook.

## Start here

Set up the environment:

```sh
uv sync
```

Open [notebooks/01_bus_departures.ipynb](notebooks/01_bus_departures.ipynb) in
VS Code and select the repository's `.venv` (`wedding-sim`) kernel, then run
the cells directly in the editor — no JupyterLab needed. `uv sync` installs
`wedding_sim` from `src/` into that same environment, so no notebook-specific
path setup is required.

## Repository structure

```text
src/wedding_sim/
  bus_departures/       # One self-contained simulation
    inputs.py           # Assumptions and parameter types
    behavioral.py       # Probabilistic operational model and optimizer
    visualization.py    # Notebook-ready charts
    README.md           # Model specification and limitations
notebooks/              # Scenario exploration and comparison
```

Future simulations, such as `guest_experience` and `bar_wait`, should use the
same shape. The simulation-level README is the authoritative description of
the model, its inputs, outputs, assumptions, and limitations.

## Command line

Run the deterministic bus schedule:

```sh
uv run wedding-sim buses
```

Add probabilistic queue trials:

```sh
uv run wedding-sim buses --trials 10000
```

See [the bus-departures model specification](src/wedding_sim/bus_departures/README.md)
for interpretation and configuration details.
