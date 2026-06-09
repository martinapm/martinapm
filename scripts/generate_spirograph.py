#!/usr/bin/env python3
"""
Genera el espirógrafo SVG para el README de @martinapm.
Calcula el progreso según los días transcurridos desde START_DATE.
Cada año completa un ciclo: una rosa matemática de 5 pétalos.
"""
 
import math
import datetime
from pathlib import Path
 
# ── Configuración ───────────────────────────────────────────────
START_DATE  = datetime.date(2025, 3, 20)   
CYCLE_DAYS  = calendar.monthrange(today.year, today.month)[1]                          
 
# Parámetros del espirógrafo — rosa de 5 pétalos
#   R=5, r=2, d=5  →  periodo = 4π  →  5 lazos exteriores
R, r, d  = 5, 2, 5
PERIOD   = 4 * math.pi
N        = 1500          # puntos totales (suavidad de la curva)
SCALE    = 22            # escala del dibujo
CX, CY   = 200, 200      # centro del canvas SVG
SVG_SIZE = 400
 

PALETTE = [
    '#1a0505', '#3b0808', '#5a2030', '#6b2d3e',
    '#8b3a50', '#a35c6e', '#c17a8a', '#d4a0a0',
    '#ecc8cc', '#f5e6e8'
]
 
# ── Helpers ──
def hex_to_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
 
def color_at(t):
    """t en [0, 1] → color interpolado de la paleta."""
    x       = t * (len(PALETTE) - 1)
    i       = min(int(x), len(PALETTE) - 2)
    f       = x - i
    r1,g1,b1 = hex_to_rgb(PALETTE[i])
    r2,g2,b2 = hex_to_rgb(PALETTE[i + 1])
    return (
        round(r1 + f * (r2 - r1)),
        round(g1 + f * (g2 - g1)),
        round(b1 + f * (b2 - b1))
    )
 
def spiro_point(t):
    """Calcula coordenadas SVG para el parámetro t."""
    x = (R - r) * math.cos(t) + d * math.cos(((R - r) / r) * t)
    y = (R - r) * math.sin(t) - d * math.sin(((R - r) / r) * t)
    return round(CX + x * SCALE, 1), round(CY + y * SCALE, 1)
 
def build_path(pts):
    return ' '.join(
        f"{'M' if j == 0 else 'L'}{p[0]},{p[1]}"
        for j, p in enumerate(pts)
    )
 
# ── Calcular progreso del día actual ───
today        = datetime.date.today()
days_elapsed = (today - START_DATE).days
day_in_cycle = days_elapsed % CYCLE_DAYS       
progress     = day_in_cycle / CYCLE_DAYS       
visible_n    = max(1, int(progress * N))
 
print(f"Día en ciclo: {day_in_cycle}/{CYCLE_DAYS}  ({round(progress*100)}%)")
 
# ── Generar todos los puntos de la curva ──
points = [spiro_point((i / N) * PERIOD) for i in range(N + 1)]
tip    = points[min(visible_n, N)]
 
# ── Construir SVG ──
CHUNK  = 8       
lines  = []
 
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" '
             f'width="{SVG_SIZE}" height="{SVG_SIZE}">')
 
# Fondo
lines.append(f'  <rect width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#0d1117"/>')
 
# Grid decorativo
lines.append('  <g opacity="0.35">')
for i in range(9):
    for j in range(9):
        lines.append(f'    <circle cx="{25 + i*44}" cy="{25 + j*44}" r="0.8" fill="#3b0808"/>')
lines.append('  </g>')
 
# Segmentos del espirógrafo 
lines.append('  <g>')
for i in range(0, visible_n, CHUNK):
    chunk = points[i : i + CHUNK + 1]
    if len(chunk) < 2:
        continue
    col    = color_at(i / N)
    path_d = build_path(chunk)
    lines.append(
        f'    <path d="{path_d}" '
        f'stroke="rgb{col}" stroke-width="1.6" '
        f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    )
lines.append('  </g>')
 
# Punta brillante 
tx, ty = tip
lines.append(f'  <circle cx="{tx}" cy="{ty}" r="10" fill="#f5e6e8" opacity="0.05"/>')
lines.append(f'  <circle cx="{tx}" cy="{ty}" r="5"  fill="#f5e6e8" opacity="0.15"/>')
lines.append(f'  <circle cx="{tx}" cy="{ty}" r="2.2" fill="#ffffff" opacity="0.9"/>')
 
# Texto sutil en la parte inferior
pct   = round(progress * 100)
label = f"day {day_in_cycle} \u00b7 {pct}% complete"
lines.append(
    f'  <text x="{SVG_SIZE // 2}" y="{SVG_SIZE - 10}" '
    f'text-anchor="middle" font-family="monospace" font-size="9" '
    f'fill="#3b0808" letter-spacing="2">{label}</text>'
)
 
lines.append('</svg>')
 
# ── Guardar archivo ──
out = Path("assets/spirograph.svg")
out.parent.mkdir(exist_ok=True)
out.write_text('\n'.join(lines), encoding='utf-8')
 
print(f"✓ Guardado en {out}  —  punta en ({tx}, {ty})")
