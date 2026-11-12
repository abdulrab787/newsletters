"""Render branded infographic PNGs from a chart spec JSON.

Usage: python tools/make_infographic.py .tmp/<slug>/charts.json

charts.json:
{
  "out_dir": ".tmp/<slug>/images",
  "charts": [
    {"id": "hero_stat", "type": "stat_cards", "title": "...",
     "cards": [{"value": "42%", "label": "...", "source": "Org, 2026"}]},
    {"id": "growth", "type": "bar" | "hbar" | "line", "title": "...",
     "labels": ["A", "B"], "values": [1, 2], "unit": "%", "source": "Org, 2026"},
    {"id": "history", "type": "timeline", "title": "...",
     "events": [{"when": "2020", "what": "..."}], "source": "..."}
  ]
}
Output: 1200px-wide PNGs (displayed at 600px in the email for retina sharpness).
"""
import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import load_brand  # noqa: E402

W_IN, DPI = 6.0, 200  # 6in * 200dpi = 1200px


def _style(brand):
    c = brand["colors"]
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "axes.edgecolor": c["muted"],
        "axes.labelcolor": c["text"],
        "xtick.color": c["muted"],
        "ytick.color": c["muted"],
        "text.color": c["text"],
    })
    return c


def _finish(fig, ax, spec, c):
    fig.patch.set_facecolor(c["card"])
    fig.text(0.04, 0.96, spec["title"], fontsize=15, fontweight="bold",
             color=c["primary"], va="top", ha="left", wrap=True)
    if spec.get("source"):
        fig.text(0.04, 0.02, f"Source: {spec['source']}", fontsize=7.5,
                 color=c["muted"], va="bottom", ha="left")


def _axes_clean(ax, c):
    ax.set_facecolor(c["card"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y" if ax.get_xlabel() == "" else "x", color=c["background"], linewidth=1)
    ax.set_axisbelow(True)


def _fmt(v, unit):
    s = f"{v:,.1f}".rstrip("0").rstrip(".") if isinstance(v, float) else f"{v:,}"
    return f"{s}{unit}" if unit in ("%",) else (f"{unit}{s}" if unit in ("$", "£", "€") else f"{s} {unit}".strip())


def chart_bar(spec, c, horizontal=False):
    h = 3.6 if not horizontal else max(3.2, 0.5 * len(spec["labels"]) + 1.8)
    fig, ax = plt.subplots(figsize=(W_IN, h))
    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.08 if not horizontal else 0.34, right=0.96)
    unit = spec.get("unit", "")
    colors = [c["accent"] if i == spec.get("highlight") else c["primary"]
              for i in range(len(spec["values"]))]
    labels = ["\n".join(textwrap.wrap(str(l), 24 if horizontal else 14)) for l in spec["labels"]]
    if horizontal:
        bars = ax.barh(labels[::-1], spec["values"][::-1], color=colors[::-1], height=0.6)
        ax.set_xlabel(" ")
    else:
        bars = ax.bar(labels, spec["values"], color=colors, width=0.6)
    _axes_clean(ax, c)
    top = max(spec["values"])
    for b, v in zip(bars, spec["values"][::-1] if horizontal else spec["values"]):
        if horizontal:
            ax.text(b.get_width() + top * 0.01, b.get_y() + b.get_height() / 2, _fmt(v, unit),
                    va="center", fontsize=9, fontweight="bold", color=c["text"])
        else:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + top * 0.02, _fmt(v, unit),
                    ha="center", fontsize=9, fontweight="bold", color=c["text"])
    (ax.set_xlim if horizontal else ax.set_ylim)(0, top * 1.15)
    ax.tick_params(axis="both", labelsize=8.5)
    _finish(fig, ax, spec, c)
    return fig


def chart_line(spec, c):
    fig, ax = plt.subplots(figsize=(W_IN, 3.6))
    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.09, right=0.95)
    x = range(len(spec["labels"]))
    ax.plot(x, spec["values"], color=c["primary"], linewidth=2.5, marker="o", markersize=6)
    ax.fill_between(x, spec["values"], color=c["primary"], alpha=0.08)
    unit = spec.get("unit", "")
    ax.annotate(_fmt(spec["values"][-1], unit), (x[-1], spec["values"][-1]),
                textcoords="offset points", xytext=(0, 10), ha="center",
                fontsize=10, fontweight="bold", color=c["accent"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(spec["labels"], fontsize=8.5)
    _axes_clean(ax, c)
    ax.set_ylim(min(0, min(spec["values"])), max(spec["values"]) * 1.2)
    _finish(fig, ax, spec, c)
    return fig


def chart_stat_cards(spec, c):
    cards = spec["cards"]
    n = len(cards)
    fig, ax = plt.subplots(figsize=(W_IN, 2.9))
    fig.subplots_adjust(top=0.72, bottom=0.12, left=0.03, right=0.97)
    ax.set_xlim(0, n)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, card in enumerate(cards):
        ax.add_patch(plt.Rectangle((i + 0.04, 0.02), 0.92, 0.96, color=c["background"], zorder=0))
        ax.add_patch(plt.Rectangle((i + 0.04, 0.02), 0.92, 0.04, color=c["accent"], zorder=1))
        ax.text(i + 0.5, 0.62, card["value"], ha="center", va="center",
                fontsize=26 if n <= 3 else 21, fontweight="bold", color=c["primary"])
        ax.text(i + 0.5, 0.28, "\n".join(textwrap.wrap(card["label"], 18 if n <= 3 else 14)),
                ha="center", va="center", fontsize=9, color=c["text"])
    _finish(fig, ax, spec, c)
    return fig


def chart_timeline(spec, c):
    events = spec["events"]
    n = len(events)
    fig, ax = plt.subplots(figsize=(W_IN, 3.4))
    fig.subplots_adjust(top=0.75, bottom=0.12, left=0.04, right=0.96)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    ax.plot([-0.4, n - 0.6], [0, 0], color=c["muted"], linewidth=2, zorder=1)
    for i, ev in enumerate(events):
        up = i % 2 == 0
        ax.scatter([i], [0], s=120, color=c["accent"], zorder=2)
        ax.text(i, 0.18 if up else -0.18, ev["when"], ha="center",
                va="bottom" if up else "top", fontsize=10, fontweight="bold", color=c["primary"])
        ax.text(i, 0.42 if up else -0.42, "\n".join(textwrap.wrap(ev["what"], 16)),
                ha="center", va="bottom" if up else "top", fontsize=8, color=c["text"])
    _finish(fig, ax, spec, c)
    return fig


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    spec_path = Path(sys.argv[1])
    cfg = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    c = _style(load_brand())
    makers = {
        "bar": chart_bar,
        "hbar": lambda s, c: chart_bar(s, c, horizontal=True),
        "line": chart_line,
        "stat_cards": chart_stat_cards,
        "timeline": chart_timeline,
    }
    for spec in cfg["charts"]:
        if spec["type"] not in makers:
            raise SystemExit(f"Unknown chart type {spec['type']!r} (id={spec['id']})")
        fig = makers[spec["type"]](spec, c)
        out = out_dir / f"{spec['id']}.png"
        fig.savefig(out, dpi=DPI, facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
