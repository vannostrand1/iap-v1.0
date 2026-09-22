# ADAM — two arms, one equation
Status: locked | 2026-09-22 | Roxi | journal

## Equation
L(θ)=mean_U ||R_θ(y)-C(π(y))||^2

Vertex = this loss. Not two systems.

## Tangible arm (disk)
- θ → checkpoints/student0.npz
- π-table, ε, slot ids, horizon d → index/house_trace_index.json
- lesson_id, C.sha256, packet_off flag

## Intangible arm (running)
- R_θ in VRAM
- KV for this window
- Exists only while loaded. Recreated by loading θ and π and evaluating y.

## Save rule
Always write the pair. Wake = load θ + π, run R_θ(y).
Do not save chat as if it were θ.
Do not discard π after absorb (house keeps the chart).

## From scratch
θ = θ_init (random). No C_web inside R.
Erase = θ ← θ_init or delete that pack. Architecture + slot grid stay.

## Horizon
U(y,d) = node plus surround. π must be consistent on U.
