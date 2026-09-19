# What changed in consolidation

The original ZIP archives and reports are preserved byte-for-byte. The active
package is a maintainable port with changes described here, not a stealth
replacement of historical source.

| Area | Historical scripts | v1 package |
|---|---|---|
| Paths | Some `/mnt/data/...` imports and global package roots | Package-relative assets |
| Grounder input | Full simulator dictionaries in several gates | Public view + counted oracle |
| Task labels | Gate 2F source actions read from supplied Transformer packet | Independent canonical convention; equality to all shipped packets tested |
| Resource loading | Module import loads packet files/global state | Explicit loading with manifest checks |
| Randomness | Several import-time/global settings | Seeds/threads set explicitly by runner |
| Pairing | World pairing; some condition-specific initialization offsets | Both legacy offsets and matched initialization, separately named |
| Optimization | Gate-specific loops | Common replay-absorption API; no implicit claim of exact Gate 2E control-loop identity |
| Checkpoints | Inconsistent persistence across prototypes | Native student-only checkpoints + reload test |
| Costs | Often called observations/interactions | Draws, unique states, batches, label probes and wire framing separated |
| Errors | Some empty-hypothesis cases implicit | Explicit failure; no silent identity/oracle fallback |

The Gate 2F world generator and grounding-query schedules have direct numerical
regression tests against the archive. Recipient training is also rerun in the
release validation. Preserve any platform/numerical differences; do not silently
rewrite old raw rows to match a port.

`archive/` is archaeology: some early/C/D scripts have unportable paths and are
not exposed as supported executable entry points. Use the active CLI/configs.
Gate 2F's standalone original source can also be run through
`scripts/run_archived_gate2f.py` for an unchanged-source comparison.
