"""Notebook-ready charts for wedding timeline simulations."""

from __future__ import annotations

from wedding_sim.timeline.simulation import TimelineResult, minutes_to_clock


_COLORS = {
    "Getting ready": "#d6a5b8",
    "Photography": "#9c89b8",
    "Ceremony": "#6b8e23",
    "Guests": "#a8b8a0",
    "Reception": "#e0a458",
    "Meal": "#4f86a6",
    "Toasts": "#c97775",
    "Dancing": "#7851a9",
    "Transportation": "#555555",
}


def plot_timeline(result: TimelineResult, *, start="08:30", end="23:00", ax=None):
    """Plot planned bars with expected and 90th-percentile simulated ends."""
    import matplotlib.pyplot as plt

    from wedding_sim.timeline.simulation import clock_to_minutes

    if ax is None:
        _, ax = plt.subplots(figsize=(13, 14))
    visible = [
        event for event in result.events
        if event.planned_start_minutes >= clock_to_minutes(start)
        and event.planned_start_minutes <= clock_to_minutes(end)
    ]
    positions = list(range(len(visible)))
    for y, event in zip(positions, visible, strict=True):
        duration = max(1, event.planned_end_minutes - event.planned_start_minutes)
        ax.barh(y, duration, left=event.planned_start_minutes, height=0.58,
                color=_COLORS.get(event.category, "#888888"), alpha=0.75)
        ax.plot(event.expected_end_minutes, y, "o", color="#222222", markersize=3)
        ax.plot([event.expected_end_minutes, event.p90_end_minutes], [y, y],
                color="#222222", linewidth=1.2)
    ax.set_yticks(positions, [event.label for event in visible], fontsize=8)
    ax.invert_yaxis()
    low, high = clock_to_minutes(start), clock_to_minutes(end)
    ticks = list(range(int(low // 60 * 60), int(high) + 1, 60))
    ax.set_xticks(ticks, [minutes_to_clock(tick) for tick in ticks], rotation=35, ha="right")
    ax.set_xlim(low, high)
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("Wedding-day timeline: planned duration and simulated finish risk", pad=14)
    ax.set_xlabel("Bar = planned duration · dot = expected finish · line end = 90th-percentile finish")
    return ax


def plot_delay_risk(result: TimelineResult, *, minimum_probability=0.01, ax=None):
    """Rank events by their chance of starting more than ten minutes late."""
    import matplotlib.pyplot as plt

    events = sorted(
        (event for event in result.events if event.over_10_minutes_late_probability >= minimum_probability),
        key=lambda event: event.over_10_minutes_late_probability,
    )
    if ax is None:
        _, ax = plt.subplots(figsize=(9, max(3.5, len(events) * 0.38)))
    ax.barh(
        [event.label for event in events],
        [event.over_10_minutes_late_probability * 100 for event in events],
        color=[_COLORS.get(event.category, "#888888") for event in events],
    )
    ax.set_xlabel("Probability of starting more than 10 minutes late (%)")
    ax.set_title("Where schedule delays accumulate")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    return ax


_HTML_STYLE = """
<style>
.wsim-cmp { --bg: #ffffff; --fg: #121417; --fg-2: #4d5159; --muted: #7d828c; --rule: #e4e5e8; --grid: #eeeff1;
  --band: #b7d3f6; --p50: #2a78d6; --actual: #eb6834; --plan: #4d5159; --critical: #d03b3b; --good: #0f7a0f;
  background: var(--bg); color: var(--fg); font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 20px; border-radius: 8px; max-width: 900px; }
.wsim-cmp h3 { margin: 0 0 4px; font-size: 18px; color: var(--fg); }
.wsim-cmp p { margin: 0 0 12px; color: var(--fg-2); max-width: 70ch; }
.wsim-cmp .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin: 14px 0 18px; }
.wsim-cmp .tile { border: 1px solid var(--rule); border-radius: 8px; padding: 10px 14px; display: grid; gap: 2px; }
.wsim-cmp .k { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.wsim-cmp .v { font: 22px ui-monospace, "SF Mono", Menlo, monospace; font-variant-numeric: tabular-nums; }
.wsim-cmp .s { font-size: 12px; color: var(--fg-2); }
.wsim-cmp .legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 12px; color: var(--fg-2); margin-bottom: 8px; }
.wsim-cmp .legend span { display: inline-flex; align-items: center; gap: 6px; }
.wsim-cmp .chart { overflow-x: auto; }
.wsim-cmp svg text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.wsim-cmp .mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
.wsim-cmp .hit { fill: transparent; }
.wsim-cmp .hit:hover { fill: var(--grid); }
.wsim-cmp table { border-collapse: collapse; width: 100%; font-size: 12px; margin-top: 10px; }
.wsim-cmp th, .wsim-cmp td { text-align: right; padding: 4px 8px; border-bottom: 1px solid var(--rule); white-space: nowrap; color: var(--fg); background: var(--bg); }
.wsim-cmp th:first-child, .wsim-cmp td:first-child { text-align: left; }
.wsim-cmp th { color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.wsim-cmp td.num { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-variant-numeric: tabular-nums; }
.wsim-cmp .flag { color: var(--critical); font-weight: 600; }
.wsim-cmp .ok { color: var(--good); font-weight: 600; }
.wsim-cmp summary { cursor: pointer; font-weight: 600; margin-top: 14px; }
</style>
"""


def _signed(value: float) -> str:
    rounded = round(value, 1)
    if rounded == 0:
        return "±0"
    text = f"{abs(rounded):.0f}" if rounded == int(rounded) else f"{abs(rounded):.1f}"
    return ("+" if rounded > 0 else "−") + text


def comparison_html(comparisons, *, window=None, title="Actual start times vs. the simulated P50 and P90") -> str:
    """Render a self-contained HTML/SVG strip chart of actual starts against the simulation.

    Each row shows the simulated P50→P90 start band and the observed start, in
    minutes relative to the planned start. Needs no JavaScript, so it displays in
    Jupyter, VS Code, and exported notebooks alike.
    """
    from html import escape
    import math

    if window is None:
        offsets = [value - item.planned_start_minutes for item in comparisons
                   for value in (item.p50_start_minutes, item.p90_start_minutes, item.actual_start_minutes)]
        window = (min(-15, 5 * math.floor(min(offsets) / 5) - 5), max(40, 5 * math.ceil(max(offsets) / 5) + 5))
    low, high = window
    step = 10 if high - low <= 60 else 20
    width, label_w, right_w, row_h, head_h, top = 860, 250, 120, 24, 30, 28
    plot_l, plot_r = label_w + 10, width - right_w - 10

    def x(minutes: float) -> float:
        clamped = max(low, min(high, minutes))
        return plot_l + (clamped - low) / (high - low) * (plot_r - plot_l)

    phases: list[tuple[str, list]] = []
    for item in comparisons:
        if not phases or phases[-1][0] != item.phase:
            phases.append((item.phase, []))
        phases[-1][1].append(item)

    parts, y = [], top
    for phase, items in phases:
        parts.append(f'<text x="8" y="{y + 20}" font-size="12" font-weight="600" fill="var(--muted)" '
                     f'letter-spacing="0.06em">{escape(phase.upper())}</text>')
        y += head_h
        for item in items:
            cy = y + row_h / 2
            d50 = item.p50_start_minutes - item.planned_start_minutes
            d90 = item.p90_start_minutes - item.planned_start_minutes
            delay = item.delay_vs_plan_minutes
            verdict = f"▲ {item.minutes_past_p90:.1f} min past P90" if item.beyond_p90 else "Within P90"
            tooltip = (f"{item.label}\nPlanned {minutes_to_clock(item.planned_start_minutes)}\n"
                       f"Sim P50 {minutes_to_clock(round(item.p50_start_minutes))} ({_signed(d50)})\n"
                       f"Sim P90 {minutes_to_clock(round(item.p90_start_minutes))} ({_signed(d90)})\n"
                       f"Actual {minutes_to_clock(item.actual_start_minutes)} ({_signed(delay)})\n{verdict}")
            if item.note:
                tooltip += f"\n{item.note}"
            parts.append(f'<g><title>{escape(tooltip)}</title>'
                         f'<rect class="hit" x="0" y="{y}" width="{width}" height="{row_h}" rx="4"/>')
            parts.append(f'<text x="{label_w}" y="{cy + 4}" text-anchor="end" font-size="13" fill="var(--fg)">'
                         f'{escape(item.label)}</text>')
            if x(d90) - x(d50) > 0.5:
                parts.append(f'<rect x="{x(d50):.1f}" y="{cy - 4}" width="{x(d90) - x(d50):.1f}" height="8" rx="4" fill="var(--band)"/>')
            parts.append(f'<line x1="{x(d50):.1f}" x2="{x(d50):.1f}" y1="{cy - 6}" y2="{cy + 6}" stroke="var(--p50)" stroke-width="2"/>')
            parts.append(f'<circle cx="{x(delay):.1f}" cy="{cy}" r="5.5" fill="var(--actual)" stroke="var(--bg)" stroke-width="2"/>')
            flag = '<tspan fill="var(--critical)" dx="6">▲</tspan>' if item.beyond_p90 else ""
            status = "on time" if delay == 0 else f"{_signed(delay)} min"
            parts.append(f'<text class="mono" x="{plot_r + 14}" y="{cy + 4}" font-size="12" fill="var(--fg-2)">{status}{flag}</text></g>')
            y += row_h
        y += 6
    height = y + 8

    grid = []
    for tick in range(low, high + 1, 5):
        is_plan = tick == 0
        grid.append(f'<line x1="{x(tick):.1f}" x2="{x(tick):.1f}" y1="{top - 6}" y2="{height - 8}" '
                    f'stroke="var({"--plan" if is_plan else "--grid"})" stroke-width="{1.5 if is_plan else 1}"'
                    f'{" stroke-dasharray=\"3 2\"" if is_plan else ""}/>')
        if tick % step == 0:
            grid.append(f'<text class="mono" x="{x(tick):.1f}" y="{top - 12}" text-anchor="middle" font-size="11" '
                        f'fill="var(--muted)">{"plan" if is_plan else _signed(tick)}</text>')
    grid.append(f'<text x="{plot_r + 14}" y="{top - 12}" font-size="11" fill="var(--muted)">actual vs plan</text>')
    svg = (f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
           f'aria-label="Actual start delay versus simulated P50 and P90 for each event">'
           + "".join(grid) + "".join(parts) + "</svg>")

    within = sum(not item.beyond_p90 for item in comparisons)
    worst = max(comparisons, key=lambda item: item.minutes_past_p90)
    tiles = [("Within P90", f"{within} / {len(comparisons)}", f"{len(comparisons) - within} events started after their simulated P90")]
    ceremony = next((item for item in comparisons if item.key == "ceremony"), None)
    if ceremony:
        tiles.append(("Ceremony", f"{_signed(ceremony.delay_vs_plan_minutes)} min",
                      f"Started {minutes_to_clock(ceremony.actual_start_minutes)}; P90 was "
                      f"{minutes_to_clock(round(ceremony.p90_start_minutes))}"))
    if worst.beyond_p90:
        tiles.append(("Largest miss past P90", f"{_signed(worst.minutes_past_p90)} min",
                      f"{worst.label} at {minutes_to_clock(worst.actual_start_minutes)}; P90 was "
                      f"{minutes_to_clock(round(worst.p90_start_minutes))}"))
    else:
        latest = max(comparisons, key=lambda item: item.delay_vs_plan_minutes)
        tiles.append(("Latest vs plan", f"{_signed(latest.delay_vs_plan_minutes)} min",
                      f"{latest.label} at {minutes_to_clock(latest.actual_start_minutes)}; planned "
                      f"{minutes_to_clock(latest.planned_start_minutes)}"))
    tile_html = "".join(f'<div class="tile"><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span>'
                        f'<span class="s">{escape(s)}</span></div>' for k, v, s in tiles)

    rows = "".join(
        f"<tr><td>{escape(item.label)}</td>"
        f'<td class="num">{minutes_to_clock(item.planned_start_minutes)}</td>'
        f'<td class="num">{minutes_to_clock(round(item.p50_start_minutes))}</td>'
        f'<td class="num">{minutes_to_clock(round(item.p90_start_minutes))}</td>'
        f'<td class="num">{minutes_to_clock(item.actual_start_minutes)}</td>'
        f'<td class="num">{_signed(item.delay_vs_plan_minutes)}</td>'
        f'<td class="num {"flag" if item.beyond_p90 else "ok"}">'
        f'{"▲ " + _signed(item.minutes_past_p90) if item.beyond_p90 else "within"}</td></tr>'
        for item in comparisons
    )
    legend = (
        '<div class="legend">'
        '<span><svg width="18" height="14"><line x1="9" y1="0" x2="9" y2="14" stroke="var(--plan)" stroke-width="1.5" stroke-dasharray="3 2"/></svg>Planned start</span>'
        '<span><svg width="30" height="14"><rect x="1" y="3" width="28" height="8" rx="4" fill="var(--band)"/>'
        '<line x1="6" y1="2" x2="6" y2="12" stroke="var(--p50)" stroke-width="2"/></svg>Simulated P50 → P90</span>'
        '<span><svg width="14" height="14"><circle cx="7" cy="7" r="5" fill="var(--actual)" stroke="var(--bg)" stroke-width="2"/></svg>Actual start</span>'
        '<span><span class="flag">▲</span>Actual later than P90</span></div>'
    )
    return (
        _HTML_STYLE + '<div class="wsim-cmp">'
        f"<h3>{escape(title)}</h3>"
        "<p>Minutes relative to each event's planned start. The band runs from the simulated median (P50) "
        "to the 90th-percentile (P90) start; the dot is the recorded start. Hover a row for clock times.</p>"
        f'<div class="tiles">{tile_html}</div>{legend}<div class="chart">{svg}</div>'
        "<details><summary>Table view</summary><table><thead><tr><th>Event</th><th>Planned</th><th>Sim P50</th>"
        f"<th>Sim P90</th><th>Actual</th><th>vs plan</th><th>vs P90</th></tr></thead><tbody>{rows}</tbody></table></details>"
        "</div>"
    )
