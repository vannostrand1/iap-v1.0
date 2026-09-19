# Public API

## Load a culture capsule

```python
from iap.resources import teacher_capsule

capsule = teacher_capsule("transformer")
print(capsule.payload_bytes)  # 241, excluding optional envelope
source_q = capsule.policy(capsule.source_states())
capsule.save("culture.iapc", framed=True)
```

`CultureCapsule.load` accepts historical 97/241-byte files or a v1 envelope.
A relational/ontology grounder requires the atlas; a policy-only packet is
sufficient for aligned or signed-permutation grounding.

## Ground, then absorb

```python
import numpy as np
import torch
from iap.tasks import make_world
from iap.grounding import ground_ontology
from iap.models import ModelSpec, make_model, save_student
from iap.absorption import absorb
from iap.resources import teacher_capsule

torch.set_num_threads(1)
world = make_world("ontology", seed=1300000)
capsule = teacher_capsule("fly")
oracle = world.oracle(36)
grounded = ground_ontology(capsule, world.public, oracle, budget=36)

spec = ModelSpec("transformer", inputs=8, actions=4, seed=1300010)
recipient = make_model(spec)
report = absorb(
    recipient, world.public.observations, grounded.targets,
    np.flatnonzero(grounded.predicted_roles),
    updates=512, seed=1300101,
)
save_student(recipient, spec, "student.pt")
print(oracle.accounting(), report.unique_states_exposed)
```

In real integrations, supply a public observation/transition structure and a
calibration adapter implementing `query(state_id) -> label`. Do not inject an
unbounded answer key. Query labels must conform to the selected grammar.

## Important boundaries

`BenchmarkWorld.labels` and `hidden_metadata` are simulator/evaluator fields.
Grounders accept only `PublicWorld` and a `CalibrationAPI`. Absorption accepts
only local observations, targets, eligible indices and optimization settings.
The optional evaluator callback observes checkpoints but its metrics are not
used by the optimizer or stopping rule. `ModelSpec` and native state are the only
objects in an exported student checkpoint.

## Add a recipient

Any compatible PyTorch `nn.Module` mapping a batch of local observations to a
batch of action values can call `absorb`. A `project()` method is optional.
The built-in checkpoint loader intentionally whitelists the three documented
architectures. A custom architecture should implement its own safe checkpoint
schema, and add factory/CLI support and tests before claiming release support.
Do not load arbitrary Python class names from packet metadata.

This API extension path is not evidence that every architecture can absorb
these conventions or that every environment admits the bounded grounders.
