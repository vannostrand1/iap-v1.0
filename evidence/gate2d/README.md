# IAP Gate 2D — Alien Cross-Architecture Cultural Transmission

## Question

Can knowledge cross both an **architecture boundary** and an **incompatible semantic interface**?

Gate 2C showed Fly ↔ MLP/Transformer transfer when inputs/actions already meant the same thing. Gate 2D removes that shared interface.

The recipient sees a fresh alien encoding:

- all 6 sensory coordinates are permuted;
- each sensory coordinate may have its sign flipped;
- the two action labels may be swapped.

The hidden mapping is never given to the grounding system or the student.

Only the same 97-byte architecture-neutral teacher packet from Gate 2C crosses the model boundary. No teacher-native weights, gradients, hidden states, topology, or replay data are transferred.

## Task

The underlying Convention Relay has 24 symbolic states: 8 three-bit contexts × 3 stages. Correct actions are defined by three different conventions (parity, endpoint XOR, majority). A full sequence succeeds only when all three stage actions are correct.

The point of the task is not visual perception or locomotion; it is to isolate semantic grounding and cultural absorption.

## Alien interface

For each replicate a fresh hidden transform is sampled:

```
alien_state[j] = sign[j] * canonical_state[perm[j]]
alien_action = canonical_action XOR action_swap
```

This mixes context and stage coordinates freely. The receiver therefore cannot assume that a particular input slot retains its teacher-side meaning.

## Autonomous grounding

The grounder is given no hidden transform ID. It uses a generic signed-permutation hypothesis class over all six coordinates:

- 6! coordinate permutations
- 2^6 sign patterns
- 2 action-label mappings

for 92,160 complete semantic hypotheses.

At each calibration step it:

1. keeps hypotheses consistent with reward evidence;
2. finds the local state on which surviving hypotheses disagree most;
3. queries one alien action and observes its reward sign;
4. removes inconsistent interpretations;
5. after the budget is exhausted, averages the teacher packet's action values over surviving meanings.

The student itself is not reward-trained during cultural absorption. Calibration rewards are used only by the grounding module.

## Grounding curve

40 fresh alien transforms were evaluated at each calibration budget for each teacher packet.

| Teacher packet | Reward queries | Mean action grounding | Mean full-sequence grounding | Perfect groundings |
|---|---:|---:|---:|---:|
| Fly | 4 | 58.65% | 11.56% | 0/40 |
| Fly | 8 | 70.94% | 30.00% | 0/40 |
| Fly | 12 | 90.94% | 75.63% | 3/40 |
| **Fly** | **16** | **100%** | **100%** | **40/40** |
| Transformer | 4 | 63.54% | 20.31% | 0/40 |
| Transformer | 8 | 77.50% | 39.69% | 0/40 |
| Transformer | 12 | 90.00% | 72.19% | 2/40 |
| **Transformer** | **16** | **100%** | **100%** | **40/40** |

Gate 2D therefore freezes **16 active calibration queries** for the cross-architecture transfer test.

## Transformer → alien Fly

Twelve fresh alien transforms were evaluated. The recipient alternates between the two fly graph substructures used in Gate 2C. After grounding, each fly receives 512 culture-only observations and no environmental reward. The packet is then removed before evaluation.

Result:

- **12/12 perfect recipients**
- mean action accuracy: **100%**
- mean complete-sequence success: **100%**

Without grounding, the same Transformer packet expressed directly in teacher coordinates corresponds to only **45.49%** target action accuracy and **7.29%** complete-sequence success on average across those alien interfaces.

A direct trained no-grounding control (4 replicates) finished at only **46.88% action / 6.25% sequence**.

## Fly → alien Transformer

Twelve fresh alien transforms were evaluated. The Transformer receives 512 culture-only observations after the same 16-query grounding procedure.

Result:

- **10/12 perfect recipients**
- mean action accuracy: **96.88%**
- bootstrap 95% interval: **92.36–100%**
- mean complete-sequence success: **91.67%**
- bootstrap 95% interval: **79.17–100%**

The two fixed-seed misses were 79.17%/50% and 83.33%/50% (action/sequence). Both alien transforms were re-run with four alternate Transformer initializations; **all 8 alternate runs reached 100% / 100%**. This localizes the misses to recipient optimization/initialization sensitivity rather than semantic-grounding failure.

Without grounding, the fly packet corresponds to only **50.35% action / 11.46% sequence** on average. A direct trained no-grounding control (4 replicates) finished at **48.96% / 9.38%**.

## Main result

Within this constrained symbolic setting, the experiment demonstrates both directions:

**Transformer knowledge → alien semantics → fly internal gains: yes.**

**Fly knowledge → alien semantics → Transformer parameters: yes, with some initialization sensitivity.**

The strongest result is Transformer → Fly: twelve independent alien interfaces, two different fly graph substructures, zero recipient reward during cultural absorption, and 12/12 perfect final behavior after the 97-byte packet is removed.

The no-grounding controls show that cross-architecture learning alone is not enough. The semantic alignment step is causally necessary under the alien interface.

## What this does and does not establish

Supported here:

- learned knowledge can cross very different model architectures;
- teacher and recipient do not need a shared input coordinate system;
- teacher and recipient do not need shared action labels;
- a small number of empirical interactions can ground the foreign packet;
- after grounding, the recipient can internalize the culture in its own parameters/gains;
- the packet can be removed at evaluation.

Still scaffolded:

- the world is only a 24-state symbolic task;
- the grounder is told to search the generic class of signed coordinate permutations plus action swap;
- this implementation exhaustively evaluates that hypothesis class rather than using Gate 1H's proposal-efficient learned generator;
- 16 calibration queries cover two thirds of the 24 symbolic states, and binary reward is highly informative;
- teacher packets were distilled over the complete canonical state manifold upstream;
- the task does not require visual perception, locomotion, or persistent recurrent memory at inference;
- fly evidence comes from two fly-derived graph substructures, not a biological population.

So Gate 2D is evidence for **architecture + representation portability within a bounded semantic transformation family**, not a universal language theorem.

## Files

- `results/grounding_sweep.csv` — 320 grounding trials (2 packets × 4 budgets × 40 transforms)
- `results/grounding_aggregate.csv` — grounding summary
- `results/transfer_raw.csv` — primary bidirectional transfer trials
- `results/transfer_aggregate.csv` — main cross-architecture summary
- `results/ungrounded_trained_controls.csv` — recipients deliberately taught without semantic grounding
- `results/initialization_sensitivity.csv` — alternate initializations for the two Fly→Transformer misses
- `packets/*.iap` — the original 97-byte teacher packets
- `PACKET_MANIFEST.json` — packet hashes
- `source/` — experiment implementation and fly model source

## Natural next gate

**Gate 2E: Non-enumerative alien culture.**

Replace the exhaustive signed-permutation interpreter with a learned/induced proposal policy from Gates 1G–1H, then move beyond signed permutations to transformations not present in the hypothesis family (mixing matrices, nonlinear monotone feature warps, larger action vocabularies). The target is successful Fly ↔ Transformer transfer where the receiver must construct the semantic mapping rather than search an explicitly enumerated family.
