# IAP Gate 2C — Cross-Architecture Cultural Transmission

## Question

Can learned knowledge cross a model-architecture boundary in both directions?

This gate uses the symbolic three-stage Convention Relay from Gate 2B to remove Doom-specific visual and motor confounds. Teachers learn from scalar reward. Their native weights, hidden states, graph structure, and training history are not transferred. Only a 97-byte quantized architecture-neutral IAP packet crosses the boundary.

During cultural absorption the recipient gets packet guidance on locally observed symbolic states but **zero environmental reward**. The packet is then removed before evaluation.

## Architectures

- **Fly:** 256-neuron FlyWire-derived recurrent rate circuit. Only positive gains on existing signed edges are trainable. Teacher has 8,084 trainable gains; recipients have 8,139 and 8,580.
- **MLP:** conventional 6→32→32→2 tanh feed-forward network, 1,346 trainable parameters.
- **Transformer:** six feature tokens plus CLS, one 24-dimensional 4-head Transformer encoder layer and a two-action head, 5,114 trainable parameters.

All three teacher architectures independently reach 100% action accuracy and 100% three-step sequence success from reward before distillation.

## Packet

Each teacher's action-value preference function on the 24-state symbolic manifold is centered/scaled, distilled into a 6→8→2 tanh network, and quantized to signed int8.

Packet size: **97 bytes** for every architecture.

All quantized packets reproduce their teacher's final action policy at 100% on all 24 states.

The canonical packets are not byte-identical: with a controlled packet-training seed, 82–86 of 97 bytes differ pairwise across Fly, MLP, and Transformer teachers. This should not be over-interpreted as a representation metric, but it confirms the experiment is not literally reusing one fixed byte string for every teacher.

## Cross-architecture results

### Fly teaches conventional architectures

The fly teacher's 97-byte packet was given to fresh recipients with no environmental reward.

| Direction | Cultural observations | Replicates | Action accuracy | Full-sequence success |
|---|---:|---:|---:|---:|
| Fly → MLP | 256 | 3/3 | **100%** | **100%** |
| Fly → Transformer | 256 | 3/3 | **100%** | **100%** |

At 128 observations, mean performance was already 94.4% action / 83.3% sequence for MLP and 93.1% / 79.2% for Transformer.

A same-bandwidth action-reversed packet drove all six conventional recipients to **0% action accuracy and 0% complete-sequence success** by 256 observations.

### Conventional architectures teach flies

Two different recipient fly graph substructures were tested, with three independent cultural-exposure streams each.

| Direction | Cultural observations | Replicates | Result |
|---|---:|---:|---|
| MLP → Fly | 512 | 6 | **6/6 at 100% action and 100% sequence** |
| Transformer → Fly | 512 | 6 | mean **97.9% action / 93.8% sequence**; 3/6 perfect |
| Transformer → Fly | ≤768 | 6 | **all six exposure streams reached 100% / 100% no later than 768 observations** |

For the four reverse-direction action-reversed controls that were run (MLP/Transformer into both fly graphs), every recipient reached **0% action accuracy and 0% sequence success** at 512 observations.

## Main finding

Within this constrained symbolic task, the learned convention is portable across radically different internal mechanisms:

**Fly → MLP: yes.**

**Fly → Transformer: yes.**

**MLP → Fly: yes.**

**Transformer → Fly: yes.**

The strongest version is culture-only: these outcomes occur without recipient environmental reward during the teaching phase, and evaluation occurs after the packet is removed. The knowledge is therefore re-instantiated in the recipient's own parameters/gains rather than remaining in an external teacher at test time.

## Architectural asymmetry

The recipient architecture affects absorption speed. MLP and Transformer recipients reached complete mastery from fly culture by 256 observations. Fly recipients required about 512 observations for MLP culture and up to 768 for Transformer culture.

This motivates a new measurable quantity: **cultural absorption efficiency** — the amount of architecture-neutral information/exposure required for one learning substrate to internalize another substrate's knowledge.

## Controls and limits

- No native weights, gradients, hidden states, or topology cross architectures.
- Teachers are trained from reward before packet creation.
- Recipients receive zero environmental rewards during cultural absorption.
- Wrong-semantic packets produce the opposite behavior, demonstrating semantic dependence rather than generic optimization help.
- Input and action semantics are still shared across architectures. This gate demonstrates **architecture independence**, not yet full semantic independence.
- The Convention Relay has 24 explicit symbolic states and does not require vision, navigation, or persistent recurrent memory at inference.
- Fly results use two fly-derived graph substructures, not a biological population.

## Next gate

**Gate 2D: Cross-Architecture + Alien Semantics.**

Use a Transformer teacher and Fly recipient (and then reverse the direction), but independently scramble the recipient's sensory coordinates and action labels. The 97-byte packet remains opaque. The recipient must use the learned semantic proposal / empirical-grounding machinery from Gates 1G–1H to discover how the foreign message maps into its own representation before absorbing it.

Success would combine two results that are currently separate:

1. knowledge is independent of model architecture; and
2. knowledge can be grounded across incompatible representations.

That would be a much stronger demonstration of an architecture- and representation-agnostic Inter-Agent Protocol.
