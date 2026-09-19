# Configuration reference

Configurations are JSON and are validated strictly by `ExperimentConfig`.
Unknown fields are rejected. All randomness is explicit.

| Field | Meaning |
|---|---|
| `name`, `purpose` | Human label and interpretation of the run |
| `family` | `aligned`, `permutation`, `relational`, or `ontology` |
| `directions` | `f2t`, `t2f`, `f2m`, `m2f`: fly/Transformer/MLP |
| `replicates`, `start_rep` | Explicit replicate range |
| `seed_base`, `direction_stride` | World seed schedule; source fly directions add the stride |
| `queries` | Number of distinct label-style calibration calls, bounded by state support |
| `outdim` | Local sensor dimension for relational/ontology families |
| `updates` | Per-direction optimizer-step/exposure-draw count |
| `conditions` | Grounded, query-only, identity, optionally wrong culture |
| `pairing` | Matched initialization or historical offsets |
| `active_grounding` | Active disagreement queries versus random distinct states |
| `threads` | Explicit Torch CPU thread count |
| `packet_paths` | Optional teacher-kind → local capsule path mapping |

Relative external packet paths are resolved against the **current working
directory**, not the config directory. The exact payload hashes enter the run
manifest and resume check. An ontology/relational packet must contain its atlas.

`wrong_culture` rotates grounded target columns by one position. It is an
incorrect-local-semantics control, not an independently learned wrong teacher.
The identity control does not use calibration labels. Query-only has zero source
packet bytes at absorption but shares the culture-selected calibration trace.

The built-in aligned configuration has no calibration, so it does not include
a query-only condition. All configurations use the same finite Convention Relay
task family; more seeds are not new conceptual task families.
