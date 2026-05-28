"""
inverter.py — CMOS inverter schematic example

Draws a two-transistor CMOS inverter:
  - PMOS (pull-up) between VDD and output
  - NMOS (pull-down) between output and GND
  - Common gate polysilicon (poly) connects both gates to input

Output: inverter.svg
"""

import os
from schematic import Schematic

OUTPUT_DIR = "output"


def draw_inverter() -> Schematic:
    """Build and return a full CMOS inverter schematic."""
    W, H = 500, 420
    sch = Schematic("CMOS Inverter", W, H)

    # ── Power rails ─────────────────────────────────────────────
    sch.vdd_rail(80, 420, 60, label="VDD")
    sch.gnd_rail(80, 420, 360, label="GND")

    # ── Transistors ─────────────────────────────────────────────
    # PMOS (pull-up) in the upper half, NMOS (pull-down) in the lower half
    pmos = sch.pmos("M2", cx=280, cy=125)
    nmos = sch.nmos("M1", cx=280, cy=275)

    # ── VDD / GND connections ───────────────────────────────────
    # PMOS top plate → VDD rail
    sch.wire(280, 60, 280, pmos.drain_y)
    sch.dot(280, 60)

    # NMOS bottom plate → GND rail
    sch.wire(280, nmos.source_y, 280, 360)
    sch.dot(280, 360)

    # ── Gate poly (common vertical gate signal bus) ─────────────
    POLY_X = 195
    gate_top = pmos.cy      # PMOS gate connection (y=125)
    gate_bot = nmos.cy      # NMOS gate connection (y=275)
    sch.wire(POLY_X, gate_top, POLY_X, gate_bot)

    # PMOS gate → poly (wire from gate centre)
    sch.wire(pmos.gate_cx, pmos.cy, POLY_X, pmos.cy)
    sch.dot(POLY_X, pmos.cy)

    # NMOS gate → poly
    sch.wire(nmos.gate_cx, nmos.cy, POLY_X, nmos.cy)
    sch.dot(POLY_X, nmos.cy)

    # ── Input signal ────────────────────────────────────────────
    IN_Y = 170
    sch.wire(60, IN_Y, POLY_X, IN_Y)
    sch.dot(POLY_X, IN_Y)
    sch.label("IN", 45, IN_Y, anchor="end")

    # ── Output signal ───────────────────────────────────────────
    OUT_Y = 210
    # Vertical connection: PMOS source → NMOS drain
    sch.wire(280, pmos.source_y, 280, nmos.drain_y)
    # Horizontal output
    sch.wire(280, OUT_Y, 440, OUT_Y)
    sch.dot(280, OUT_Y)
    sch.label("OUT", 450, OUT_Y, anchor="start")

    return sch


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sch = draw_inverter()
    path = os.path.join(OUTPUT_DIR, "inverter.svg")
    sch.save(path)
    print(f"Inverter schematic saved → {path}")
    print(f"Canvas: {sch.width}×{sch.height}")


if __name__ == "__main__":
    main()
