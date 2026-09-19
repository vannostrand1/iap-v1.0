# IAP Gate 2E — Unknown Semantic Physics via Relational Grounding

## Result

**Primary 8-D condition: passed.**

Gate 2D still assumed that the alien interface belonged to a known 92,160-member family of signed coordinate permutations plus action relabeling. Gate 2E removes that transform dictionary.

The recipient now sees a dense nonlinear alien sensor code:

`Y = normalize(tanh(1.15 * (X A^T + b)) + 0.12 * (X B^T)^3 / (1 + (X B^T)^2))`

where `A`, `B`, and `b` are freshly randomized for each replicate. No teacher coordinate is preserved directly. Local context identities are also permuted and the two action labels may be swapped.

The successful grounder does **not** try to invert this physics. Instead it aligns the teacher and recipient through shared temporal/relational structure: both worlds contain eight anonymous three-node chains. A small source relational atlas is transmitted with the teacher policy packet, while the recipient observes its own local chain structure. Active reward queries eliminate incompatible chain correspondences and action-label conventions using perfect-matching feasibility. The raw alien features are treated as opaque symbols during semantic grounding.

## Cultural payload

- teacher policy packet: **97 bytes**
- source relational atlas: **144 bytes** (24 states × 6 signed int8 coordinates, ordered as eight anonymous 3-node chains)
- total semantic payload: **241 bytes**, excluding transport/container framing

The atlas contains no mapping into recipient coordinates and no recipient action labels. It does encode the teacher-side relational state support, so Gate 2E trades a slightly larger self-describing message for a much broader semantic mismatch.

## Grounding confirmation

100 random alien worlds per teacher packet at each query budget:

| Teacher packet | Reward queries | Mean action grounding | Mean full-sequence grounding | Perfect worlds |
|---|---:|---:|---:|---:|
| Transformer | 14 | 96.33% | 90.25% | 48/100 |
| Transformer | 16 | 99.83% | 99.50% | 96/100 |
| **Transformer** | **18** | **100%** | **100%** | **100/100** |
| Fly | 14 | 94.88% | 86.75% | 32/100 |
| Fly | 16 | 99.88% | 99.63% | 97/100 |
| **Fly** | **18** | **100%** | **100%** | **100/100** |

Thus the frozen transfer confirmation uses 18 active calibration rewards.

## Cross-architecture transfer confirmation

Each recipient gets 512 zero-environment-reward cultural observations after grounding. The culture packet is removed before evaluation.

| Direction | Condition | Mean action accuracy | Mean complete-sequence success | Perfect recipients |
|---|---|---:|---:|---:|
| Transformer → Fly | **Grounded culture** | **98.61%** | **95.83%** | **9/12** |
| Transformer → Fly | Same 18 queries, no packet | 85.07% | 64.58% | 0/12 |
| Transformer → Fly | Packet without grounding | 57.29% | 17.71% | 0/12 |
| Fly → Transformer | **Grounded culture** | **100%** | **100%** | **12/12** |
| Fly → Transformer | Same 18 queries, no packet | 88.54% | 73.96% | 0/12 |
| Fly → Transformer | Packet without grounding | 48.61% | 17.71% | 0/12 |

Paired bootstrap intervals for grounded culture minus the query-only/no-packet control are positive in both directions:

- Transformer → Fly action: +13.54 points, 95% CI **+10.76 to +16.32**
- Transformer → Fly sequence: +31.25 points, **+23.96 to +38.54**
- Fly → Transformer action: +11.46 points, **+8.68 to +14.93**
- Fly → Transformer sequence: +26.04 points, **+21.88 to +30.21**

The calibration rewards alone therefore do not explain the transfer.

## 5-D non-invertible stress test

The alien sensor interface was then compressed from a six-dimensional source space to five nonlinear mixed channels. There is no globally invertible 6-D→5-D coordinate transformation, although the finite 24 task states remain distinguishable.

Grounding still stayed at **100% / 100%** because it is relational rather than coordinate-based.

| Direction | Action after 512 culture observations | Sequence success | Perfect |
|---|---:|---:|---:|
| Transformer → Fly | **86.81%** | **66.67%** | 0/12 |
| Fly → Transformer | **100%** | **100%** | 12/12 |

This cleanly separates two problems: semantic grounding still works, but the fly has difficulty *absorbing* the compressed foreign sensor code at the fixed exposure budget. The Transformer does not show that limitation here.

## Development negatives retained

Two more literal Gate-2E approaches were tested first:

1. A generic neural semantic adapter trained through the frozen packet and sparse reward labels tended to behave like a local classifier and generalized only around the 70–80% range in early pilots.
2. Evolutionary program search over invertible primitives always had a true inverse available in its language, but sparse rewards admitted many empirically perfect programs that disagreed on unqueried states.

Those failures motivated the relational solution. The key lesson is that semantic equivalence can be established through task structure without recovering the raw coordinate physics.

## What Gate 2E establishes

Within this bounded Convention Relay environment:

- knowledge crosses **Fly ↔ Transformer** architecture boundaries;
- the recipient need not share the teacher's sensory coordinates;
- no fixed coordinate-transform dictionary is used;
- dense nonlinear alien features can be treated as opaque;
- a tiny relationally self-describing cultural message plus active empirical grounding supplies useful behavior beyond the queried rewards themselves.

## Remaining scaffold

Gate 2E is **not** universal semantics. The teacher and recipient still share an observable relational task structure: eight three-step chains. The message also carries a 144-byte teacher-side relational atlas. The grounder assumes that source and recipient state graphs are related by a bijection at the chain level, plus an unknown binary action relabeling.

The next hard gate is therefore to relax the shared relational ontology itself: different graph granularities, latent/missing states, extra recipient states, many-to-one concepts, and more than two actions.
