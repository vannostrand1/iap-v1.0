# IAP Gate 2F — Cross-Ontology Cultural Transmission

Gate 2F tests whether an architecture-neutral cultural message can cross not only neural architectures and sensor encodings, but a mismatch in **what counts as a state and what counts as an action**.

## Headline result

**Primary Gate 2F passed inside the bounded ontology family.**

The teacher has 24 conceptual states and 2 abstract actions. A random recipient world has about 67 local perceptual states on average, 48 of which are actionable, and 4 primitive actions. Each teacher concept expands into multiple recipient states, nuisance states have no teacher-action analogue, and each teacher action becomes an ordered two-action recipient macro.

After 36 active calibration queries, ontology grounding was perfect in a 40-world confirmation:

| Culture source | Worlds | Primitive-action grounding | Complete macro sequences | Role grounding |
|---|---:|---:|---:|---:|
| Transformer packet | 20 | **100%** | **100%** | **100%** |
| Fly packet | 20 | **100%** | **100%** | **100%** |

### Fly teacher -> alien Transformer

Six fresh random recipient ontologies, 512 cultural observations, zero post-calibration environmental reward during absorption:

| Condition | Primitive-action accuracy | Complete six-action sequences |
|---|---:|---:|
| **Grounded culture** | **100.0%** | **100.0%** |
| Same calibration, no packet | 57.29% | 4.17% |
| Packet without ontology grounding | 24.65% | 0.0% |

Grounded culture minus same-query/no-packet:
- action accuracy: **+42.71 points**, paired bootstrap 95% interval **+38.19 to +47.22**;
- complete sequences: **+95.83 points**, interval **+91.67 to +100.00**.

### Transformer teacher -> alien Fly

Six fresh random recipient ontologies, alternating the two recipient fly graph substructures, 1,024 cultural observations:

| Condition | Primitive-action accuracy | Complete six-action sequences |
|---|---:|---:|
| **Grounded culture** | **99.65%** | **97.92%** |
| Same calibration, no packet | 62.85% | 2.08% |
| Packet without ontology grounding | 21.18% | 0.0% |

Five of six cultured flies reached 100% / 100%; the remaining fly missed one of 48 primitive decisions and finished at 97.92% action accuracy / 87.5% complete-sequence success.

Grounded culture minus same-query/no-packet:
- action accuracy: **+36.81 points**, paired bootstrap 95% interval **+33.33 to +39.93**;
- complete sequences: **+95.83 points**, interval **+91.67 to +100.00**.

## What actually changed ontologically?

The source says, conceptually:

```text
context C
  stage 0 -> abstract action A
  stage 1 -> abstract action B
  stage 2 -> abstract action A
```

A recipient might instead experience:

```text
local state 0  : nuisance
local state 1  : macro primitive 3   \
local state 2  : nuisance             > teacher stage 0
local state 3  : macro primitive 1   /
local state 4  : macro primitive 0   \
local state 5  : macro primitive 2    > teacher stage 1
local state 6  : nuisance            /
...
```

There is no one-to-one state correspondence, and source action `A` does not mean recipient primitive action `A`. The grounder must infer the temporal expansion, nuisance states, context correspondence, and macro codebook.

## Grounding curve

The lower-budget curve is exploratory (five worlds per point); the 36-query row is the 20-world-per-teacher confirmation.

| Teacher culture | Calibration queries | Primitive actions | Complete macros |
|---|---:|---:|---:|
| Transformer | 12 | 38.33% | 0.0% |
| Transformer | 20 | 77.08% | 20.0% |
| Transformer | 28 | 96.67% | 82.5% |
| **Transformer** | **36** | **100%** | **100%** |
| Fly | 12 | 31.67% | 0.0% |
| Fly | 20 | 66.25% | 5.0% |
| Fly | 28 | 95.42% | 75.0% |
| **Fly** | **36** | **100%** | **100%** |

Ontology translation therefore requires materially more calibration than Gate 2E's cross-representation grounding. That is expected: the receiver is resolving a temporal transducer and action macro code, not merely finding corresponding states.

## Why the no-packet control matters

The 36 calibration queries do not themselves specify the full recipient policy. In the six transfer worlds they expose the correct primitive action for only about **22 of the 48 actionable states on average**; the remaining queries mostly identify nuisance states.

A model trained for the same number of optimizer updates on those calibration labels alone remains far below the culturally transferred recipient. The packet is supplying behavior on the unqueried portion of the local ontology.

## Culture payload

The cultural capsule remains **241 bytes**:
- 97-byte quantized architecture-neutral policy;
- 144-byte source relational atlas.

No native Fly or Transformer weights are transmitted. Teacher checkpoints are included only for provenance/reproduction; recipients never read them during transfer.

## Important boundary

Gate 2F is **cross-ontology transfer inside a bounded ontology grammar**, not universal ontology discovery.

The interpreter is told the generic *kind* of mismatch it may face: concepts may expand into 2–3 local states, nuisance states may occur, and abstract binary actions may become ordered length-2 macros over four primitives. It has to discover the actual ontology instance, but it does not invent an arbitrary ontology language from scratch.

Also, calibration queries return the correct primitive action or `nuisance`; they are label-style probes rather than single binary reward bits. They correspond to at most four primitive reward tests each if implemented through trial-and-error.

## Files

- `PROTOCOL.md` — frozen confirmation protocol and caveats.
- `source/gate2f_experiment.py` — self-contained grounding and transfer experiment.
- `source/internal_model.py` — fly-derived rate circuit.
- `packets/` — exact 97-byte teacher packets and 241-byte cultural capsules.
- `teachers/` — teacher checkpoints for provenance only.
- `data/` — recipient fly graph substructures.
- `results/gate2f_grounding_raw.csv` — grounding trials.
- `results/gate2f_grounding_aggregate.csv` — grounding summary.
- `results/gate2f_transfer_raw.csv` — paired transfer trials.
- `results/gate2f_transfer_aggregate.csv` — transfer summary.
- `results/gate2f_paired_deltas.csv` — paired bootstrap effect estimates.

## Reproduction examples

```bash
pip install -r requirements.txt
python source/gate2f_experiment.py --mode ground --teacher transformer --budget 36 --reps 3 --out ground.csv
python source/gate2f_experiment.py --mode transfer --direction f2t --reps 3 --steps 512 --out f2t.csv
python source/gate2f_experiment.py --mode transfer --direction t2f --reps 3 --steps 1024 --out t2f.csv
```
