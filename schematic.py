"""
schematic.py — Circuit schematic drawing library
Pure Python + SVG, zero external dependencies.

Provides a clean API for describing circuit connectivity and generating
scalable SVG schematics suitable for web embedding or print.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# ─── SVG Low-Level Primitives ────────────────────────────────────────

PX = 2  # default stroke width


def _line(x1, y1, x2, y2, **kw):
    a = f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
    a += f' stroke="{kw.pop("stroke", "black")}" stroke-width="{kw.pop("sw", PX)}"'
    if kw.get("dash"):
        a += f' stroke-dasharray="{kw.pop("dash")}"'
    for k, v in kw.items():
        a += f' {k.replace("_", "-")}="{v}"'
    return f"<line {a}/>"


def _circle(cx, cy, r, **kw):
    a = f'cx="{cx}" cy="{cy}" r="{r}"'
    fill = kw.pop("fill", "none")
    a += f' fill="{fill}" stroke="{kw.pop("stroke", "black")}" stroke-width="{kw.pop("sw", PX)}"'
    for k, v in kw.items():
        a += f' {k.replace("_", "-")}="{v}"'
    return f"<circle {a}/>"


def _text(x, y, text, **kw):
    a = f'x="{x}" y="{y}"'
    font = kw.pop("font", "Arial, sans-serif")
    size = kw.pop("size", 14)
    anchor = kw.pop("anchor", "start")
    fill = kw.pop("fill", "black")
    a += f' text-anchor="{anchor}" font-family="{font}" font-size="{size}" fill="{fill}"'
    for k, v in kw.items():
        a += f' {k.replace("_", "-")}="{v}"'
    return f"<text {a}>{text}</text>"


def _path(d, **kw):
    a = f'd="{d}"'
    a += f' fill="{kw.pop("fill", "none")}" stroke="{kw.pop("stroke", "black")}" stroke-width="{kw.pop("sw", PX)}"'
    if kw.get("join"):
        a += f' stroke-linejoin="{kw.pop("join")}"'
    for k, v in kw.items():
        a += f' {k.replace("_", "-")}="{v}"'
    return f"<path {a}/>"


# ─── Element Base ────────────────────────────────────────────────────

class Element:
    """Base class for all drawable schematic elements."""
    def svg(self) -> str:
        raise NotImplementedError


# ─── Wire ────────────────────────────────────────────────────────────

@dataclass
class Wire(Element):
    """A continuous wire made of one or more connected segments."""
    points: List[Tuple[float, float]] = field(default_factory=list)

    @staticmethod
    def h(x1: float, x2: float, y: float) -> "Wire":
        return Wire().to(x1, y).to(x2, y)

    @staticmethod
    def v(x: float, y1: float, y2: float) -> "Wire":
        return Wire().to(x, y1).to(x, y2)

    def to(self, x: float, y: float) -> "Wire":
        self.points.append((x, y))
        return self

    def svg(self) -> str:
        if len(self.points) < 2:
            return ""
        d = f"M {self.points[0][0]} {self.points[0][1]}"
        for p in self.points[1:]:
            d += f" L {p[0]} {p[1]}"
        return _path(d, join="round")


# ─── Junction Dot ────────────────────────────────────────────────────

@dataclass
class Junction(Element):
    """A filled circle marking a wire junction."""
    x: float
    y: float
    r: int = 3

    def svg(self) -> str:
        return _circle(self.x, self.y, self.r, fill="black", stroke="none")


# ─── Label ───────────────────────────────────────────────────────────

@dataclass
class Label(Element):
    """Text label on the schematic."""
    text: str
    x: float
    y: float
    anchor: str = "start"
    size: int = 14

    def svg(self) -> str:
        return _text(self.x, self.y, self.text, anchor=self.anchor, size=self.size)


# ─── MOSFET Transistor ───────────────────────────────────────────────

class Transistor(Element):
    """CMOS transistor symbol (NMOS or PMOS).

    Uses the standard two-vertical-line representation:
      - Right vertical (longer)  = channel / body
      - Left  vertical (shorter) = gate electrode
      - Top / bottom horizontals = current-terminal plates
      - PMOS adds a bubble at the gate output.

    Layout geometry (all relative to center *cx, cy*):

        ┌──── drain plate (top) ────┐
        │     │              │      │
        │  gate line      body line │
        │  (shorter)      (taller)  │
        │     │              │      │
        └──── source plate (bot) ───┘

    Ports (for wire connection queries):
      - gate_x   — centre of the gate caps (left edge)
      - drain_y  — y of the top (drain) plate
      - source_y — y of the bottom (source) plate
    """

    W: int = 36       # plate width (full)
    H: int = 32       # body height (full)
    GW: int = 10      # gate offset from centre (to the left)
    GH: int = 20      # gate-electrode height
    CAP: int = 4      # gate-cap overhang
    BW: int = 2       # body offset from centre (to the right)
    BR: int = 5       # PMOS bubble radius

    def __init__(self, kind: str, name: str, cx: float, cy: float):
        assert kind in ("nmos", "pmos"), f"unknown transistor kind: {kind}"
        self.kind = kind
        self.name = name
        self.cx = cx
        self.cy = cy

    # ── Port helpers (for connecting wires) ──────────────────────

    @property
    def gate_cx(self) -> float:
        """X of the gate-electrode vertical (wire connection point)."""
        return self.cx - self.GW

    @property
    def gate_x(self) -> float:
        """Leftmost x of the gate cap (kept for compat)."""
        return self.cx - self.GW - self.CAP

    @property
    def drain_y(self) -> float:
        return self.cy - self.H // 2

    @property
    def source_y(self) -> float:
        return self.cy + self.H // 2

    @property
    def drain_left(self) -> float:
        return self.cx - self.W // 2

    @property
    def drain_right(self) -> float:
        return self.cx + self.W // 2

    # ── SVG rendering ────────────────────────────────────────────

    def svg(self) -> str:
        cx, cy = self.cx, self.cy
        h2 = self.H // 2
        w2 = self.W // 2
        gh2 = self.GH // 2
        gx = cx - self.GW

        parts = [
            # drain plate (top)
            _line(cx - w2, cy - h2, cx + w2, cy - h2),
            # source plate (bottom)
            _line(cx - w2, cy + h2, cx + w2, cy + h2),
            # body (channel) — vertical, centred-right
            _line(cx + self.BW, cy - h2 + 3, cx + self.BW, cy + h2 - 3),
            # gate electrode — vertical, centred-left
            _line(gx, cy - gh2, gx, cy + gh2),
            # gate caps (top & bottom dashes)
            _line(gx - self.CAP, cy - gh2, gx + self.CAP, cy - gh2),
            _line(gx - self.CAP, cy + gh2, gx + self.CAP, cy + gh2),
        ]

        # PMOS bubble — drawn on the gate line itself (centered at gx)
        if self.kind == "pmos":
            parts.append(
                _circle(gx, cy, self.BR, fill="white", stroke="black")
            )

        # Name label
        parts.append(
            _text(cx, cy + h2 + 18, self.name,
                  anchor="middle", size=12)
        )

        return "\n".join(parts)


# ─── Power Rail (VDD / GND) ──────────────────────────────────────────

@dataclass
class PowerRail(Element):
    """Horizontal power rail (VDD) or ground rail with ground symbol."""
    x1: float
    x2: float
    y: float
    kind: str = "vdd"          # "vdd" | "gnd"
    label: str = ""

    def svg(self) -> str:
        lines = [_line(self.x1, self.y, self.x2, self.y, sw=3)]

        if self.kind == "gnd":
            # Ground symbol: three cascading bars at left end
            cx = self.x1
            for i, w in enumerate([16, 11, 6]):
                lines.append(_line(cx - w // 2, self.y + 4 + i * 4,
                                   cx + w // 2, self.y + 4 + i * 4))
        # label — VDD above rail, GND below rail
        txt = self.label or self.kind.upper()
        dy = -5 if self.kind == "vdd" else 18
        lines.append(
            _text(self.x2 + 10, self.y + dy, txt, anchor="start", size=14)
        )
        return "\n".join(lines)


# ─── Schematic Canvas ────────────────────────────────────────────────

class Schematic:
    """Holds a collection of elements and renders them to SVG."""

    def __init__(self, title: str = "", width: int = 500, height: int = 350):
        self.title = title
        self.width = width
        self.height = height
        self.elements: List[Element] = []

    def add(self, el: Element) -> Element:
        self.elements.append(el)
        return el

    # ── Convenience helpers ───────────────────────────────────

    def wire(self, x1: float, y1: float, x2: float, y2: float) -> Wire:
        return self.add(Wire().to(x1, y1).to(x2, y2))

    def label(self, text: str, x: float, y: float,
              anchor="start", size=14) -> Label:
        return self.add(Label(text, x, y, anchor=anchor, size=size))

    def dot(self, x: float, y: float, r: int = 3) -> Junction:
        return self.add(Junction(x, y, r=r))

    def nmos(self, name: str, cx: float, cy: float) -> Transistor:
        return self.add(Transistor("nmos", name, cx, cy))

    def pmos(self, name: str, cx: float, cy: float) -> Transistor:
        return self.add(Transistor("pmos", name, cx, cy))

    def vdd_rail(self, x1: float, x2: float, y: float,
                 label: str = "VDD") -> PowerRail:
        return self.add(PowerRail(x1, x2, y, kind="vdd", label=label))

    def gnd_rail(self, x1: float, x2: float, y: float,
                 label: str = "GND") -> PowerRail:
        return self.add(PowerRail(x1, x2, y, kind="gnd", label=label))

    # ── SVG output ────────────────────────────────────────────

    def svg(self) -> str:
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}">',
            '<rect width="100%" height="100%" fill="white"/>',
        ]
        if self.title:
            parts.append(
                _text(self.width / 2, 25, self.title,
                      anchor="middle", size=16, font="Arial, sans-serif")
            )
        for el in self.elements:
            s = el.svg()
            if s:
                parts.append(s)
        parts.append("</svg>")
        return "\n".join(parts)

    def save(self, path: str):
        with open(path, "w") as f:
            f.write(self.svg())

    def _repr_html_(self) -> str:
        return self.svg()
