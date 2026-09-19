# IAP Gate 2B — Cultural Convention Relay

## Why this replaces Doom for the transfer test

The Doom experiments confound knowledge transfer with visual recognition and motor control. This environment removes those bottlenecks while retaining a sequential cultural-learning problem.

Each episode/context is one of eight explicit 3-bit symbolic contexts. The agent must make three stage-specific binary choices. The three conventions are nonlinear (parity, endpoint XOR, majority). A complete ritual succeeds only when all three choices are correct.

The fly is the same 256-neuron FlyWire-derived rate circuit used in the internal-gain experiments. Only existing-edge `log_gain` is trainable. Different recipient flies use different real graph subgraphs and different fixed sensory/motor assignments.

## Teacher

Teacher fly 7101 learns the full convention from scalar reward using the prior confirmed internal-gain update regime: replay capacity 256, Adam lr 0.03, epsilon 0.25, and reward delivered after three subsequent decisions.

Teacher reached 100% action accuracy and 8/8 complete sequences by 512 reward-bearing decisions and retained 100% through the full development run.

## Cultural packet

Teacher action-value preferences over the symbolic state manifold are distilled to a tiny 6→8→2 tanh network and quantized to int8.

Raw packet size: **97 bytes**.

The quantized packet reproduces the teacher's action policy at **100%** on all 24 context/stage states.

## Frozen confirmation

Recipients: fly 7102 / graph 223 and fly 7103 / graph 239.

Three fresh learning-stream seeds per recipient (six paired streams total).

Conditions:
- scratch: no packet exposure
- culture: 256 packet-guided state observations, no environmental rewards
- wrong culture: same packet budget with action semantics reversed

After the 256-observation exposure, the packet is removed completely. All variants then receive the same 512-decision local learning protocol with three-decision delayed reward and 10% reward-sign noise.

### Aggregate results

| condition | post-culture action acc | post-culture full-sequence success | action-learning AUC | sequence-learning AUC | final action acc | final full-sequence success |
|---|---:|---:|---:|---:|---:|---:|
| scratch | 47.92% | 6.25% | 65.36% | 27.99% | 79.17% | 47.92% |
| culture | **74.31%** | **47.92%** | **84.20%** | **60.55%** | **96.53%** | **89.58%** |
| wrong culture | 23.61% | 0.00% | 63.45% | 23.18% | 82.64% | 56.25% |

Paired culture-minus-scratch bootstrap intervals over the six matched learning streams:
- post-exposure action accuracy: **+26.39 pp**, 95% interval **+9.72 to +43.06**
- post-exposure sequence success: **+41.67 pp**, interval **+22.92 to +60.42**
- action-accuracy learning AUC: **+18.84 pp**, interval **+14.50 to +24.07**
- sequence-success learning AUC: **+32.55 pp**, interval **+23.83 to +46.74**
- final action accuracy at 512 local decisions: **+17.36 pp**, interval **+8.33 to +25.00**
- final sequence success: **+41.67 pp**, interval **+22.92 to +58.33**

The wrong-culture packet strongly changes the receiving flies immediately (post-exposure action accuracy is -24.31 pp vs scratch), but 512 local reward decisions can partially overwrite the bad convention. Its learning-AUC difference from scratch is not clearly separated from zero in this small confirmation.

## Interpretation boundary

This demonstrates transfer of a learned sequential symbolic convention into persistent internal fly gains and subsequent sample-efficiency improvement. It does **not** demonstrate visual recognition, navigation, autonomous semantic grounding, or biological learning. The six paired learning streams come from only two recipient graph subgraphs, so bootstrap intervals describe these runs and should not be interpreted as population-level biological uncertainty.

## Files

- `teacher_97b.iap`: exact 97-byte quantized cultural packet
- `teacher_fly_state.pt`: trained teacher fly internal state
- `source/teacher_train.py`: teacher-learning development script
- `source/packet_absorption_dev.py`: packet distillation/absorption development
- `source/confirmation.py`: frozen small confirmation
- `results/aggregate.csv`: compact aggregate
- `results/final_results.json`: paired deltas, raw runs, and bootstrap summaries
