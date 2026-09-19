# Method: IAP v1.0

## Implemented object

IAP v1.0 implements a particular family of **behavioral transfer experiments**:
a teacher policy is distilled into a portable small surrogate, interpreted in
a recipient's local interface using calibration evidence, and distilled again
into a recipient's native trainable parameters. It is not an arbitrary-model
communication protocol or a universal language.

The runtime stages are:

```text
teacher-side learner -> compact policy + optional source atlas
                              |
public recipient observations/chain structure + counted calibration oracle
                              |
                    bounded empirical grounder
                              |
                    local behavioral targets
                              |
                    native recipient training
                              |
                    packet-free checkpoint
```

### 1. Teacher-side compression

Let `T(x)` be the teacher's action-value vector. Center each row, then divide
by the maximum absolute centered value over the 24-state source support.
A 6→8→2 tanh network fits those values by mean squared error and is quantized
with per-tensor float32 scales and signed int8 coefficients. This stage uses
the teacher's outputs, not recipient labels. `iap distill` rebuilds this stage
from a supplied teacher checkpoint; `iap train-teacher` first trains a new
teacher by chosen-action reward regression.

The portable policy contains **surrogate-network weights**. The stronger
accurate statement is that no *native teacher* weights, gradients, hidden
activations, connectivity or replay buffer are copied into the recipient.
The packet is not weight-free and does not avoid teacher-induced action targets.

### 2. Grounding

For a capsule `C` and public recipient view `V`, the grounder maintains feasible
interpretations of the source policy in the local interface. It chooses a
local state whose predicted labels disagree across remaining interpretations,
queries the declared calibration oracle, and eliminates inconsistent hypotheses.

- **Aligned:** input and action meanings are already shared; no calibration.
- **Permutation:** enumerate 6! × 2^6 observation maps and 2 action swaps.
- **Relational:** match eight ordered three-node local chains to source chains,
  with an unknown binary action relabeling; coordinates need not be inverted.
- **Ontology:** jointly match chains and enumerate the stated expansion/macro
  family: three source stages, expansions of length 2 or 3, exactly two ordered
  actionable substates, optional nuisance states, and a permutation of four
  primitives forming two length-2 macros.

The last two grounders use perfect-matching feasibility to reject incompatible
chain correspondences. Their votes average feasible edge/pattern contributions;
they are **not an exact probabilistic posterior over all complete mappings**.
The ontology grammar is authored. It is not autonomously induced by this release.

`PublicWorld` has only observations, chains and action count. Hidden labels and
source correspondences are owned by `BenchmarkWorld`, outside the grounding
interface. `QueryOracle` is the only label path. It logs each query. This is a
cleaner implementation boundary than passing the full simulator dictionary to
the grounder, as several earlier scripts did.

### 3. Native absorption

On local observations `y`, the grounded target `q_C(y)` supervises the recipient:

`L(theta) = mean(||R_theta(y) - q_C(y)||^2)`.

An exposure draw appends one sampled state/target to replay. Each step samples
up to 32 replay entries and performs one Adam update with gradient clipping.
The fly additionally projects its log gains into [-3, 3]. The models are not
parameter-matched or training-cost matched across architectures.

Only the fly's `log_gain` parameter may change. Its normalized base signed edges,
sensory drive, motor readout and edge indices must remain byte-identical. MLP
and Transformer recipients update their ordinary weights.

No new environmental reward is used in this absorption phase. The earlier
calibration phase **does** provide supervised information, so the whole
procedure is not reward-free or label-free.

### 4. Evaluation

Save only the recipient model specification and native state. Reload it and
compute decisions without loading a packet, teacher or grounder. Action accuracy
is evaluated on the finite local support. Sequence success means all relevant
stage/primitive decisions for a context are correct. Nuisance states are ignored
in the recipient's action/sequence metric; only the grounder predicts their role.

Packet removal and cross-architecture distillation are not, on their own,
distinctions from ordinary knowledge distillation. The candidate contribution
is the combined bounded grounding/translation/absorption pipeline, which still
requires direct comparison against relevant prior methods before novelty or
superiority claims can be made.

## Source basis

The original reports and source are retained under `evidence/gate2c` through
`evidence/gate2f` and `archive/`. The API is a refactor, not a claim that the
historical gates all used one identical algorithm. See `API_CHANGES.md`.
