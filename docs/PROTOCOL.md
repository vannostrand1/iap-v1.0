# Frozen software configuration and experimental interpretation

Version: IAP 1.0.0. Software freeze date: 2026-09-19.

## Historical versus new runs

The supplied historical Gate 2F uses six ontology/stream seeds per direction,
36 action-or-nuisance calibration labels, 512 Fly→Transformer absorption steps,
and 1,024 Transformer→Fly steps. Original source/report/CSV files are immutable
under `archive/` and `evidence/`.

`configs/gate2f_historical.json` reuses that source seed schedule and original
condition seed offsets for numerical regression. It is not a new independent
confirmation. An audit found that the historical comparison is paired by world,
not by identical initialization: conventional control models use different
initial seeds. Fly mappings are fixed by recipient graph assignment.

`configs/gate2f_matched.json` uses identical initial model state and replay RNG
seed across conditions on the historical worlds. This is a **changed control
protocol**, clearly separated from the old result. Other modern configurations
also use matched initialization unless explicitly stated otherwise.

`configs/fresh_confirmation.json` reserves 24 new recipient worlds per direction
starting at seed base 9,000,000, with matched initialization, three original
conditions plus a wrong-target control. It still uses the fixed supplied
teacher packets: it is a prospective **fixed-teacher** replication, not a
fresh-teacher or fresh-task-family study. This release does not relabel those
unrun configurations as results.

## Registered outputs

Every run writes config/source hashes; runtime versions; exact capsule hashes;
all calibration queries and labels; public observations with a separate
truth-only evaluation fixture; native student checkpoints; initial/final state
hashes; loss/learning checkpoints; optimizer steps; replay batch examples;
unique states exposed; aggregation; and paired effect estimates.

The wrong-culture v1 condition deliberately rotates the **grounded local action
targets**. It does not pretend that an incorrect source packet necessarily
survives calibration. The ungrounded condition ignores translation; query-only
uses the same revealed actionable labels but not the packet. No additional
reward is supplied during absorption. Nuisance labels are recorded but not
trained as an extra recipient action in the four-action model.

## Statistical unit and scope

Aggregate over independent world/stream replicates, not over individual states
as though they were independently trained learners. The paired bootstrap is
conditional on fixed teacher checkpoints, fixed small task family, and two
recipient graph assignments from one source connectome. It is not a confidence
interval over biological populations or arbitrary teacher architectures.

For one replicate, the release reports no bootstrap interval. Missing pairs and
duplicate run keys are errors. The release does not silently promote a
completed computation to a gate pass; a publication confirmation must predeclare
an endpoint, sample size, hypothesis test and allowable development changes.

Preserve the negative Doom live result. No amount of symbolic success changes
its outcome. A future full-level/perception study belongs to another protocol.
