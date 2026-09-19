"""Use the public IAP API with a custom PyTorch recipient, without registry changes."""
import numpy as np
import torch
from torch import nn
from iap.absorption import absorb
from iap.grounding import ground_relational
from iap.models import predict
from iap.resources import teacher_capsule
from iap.tasks import make_world


def main():
    torch.set_num_threads(1)
    torch.manual_seed(101)
    world = make_world("relational", 250000)
    capsule = teacher_capsule("fly")
    oracle = world.oracle(18)
    translation = ground_relational(capsule, world.public, oracle, budget=18)
    recipient = nn.Sequential(nn.Linear(8, 48), nn.Tanh(), nn.Linear(48, 2))
    report = absorb(recipient, world.public.observations, translation.targets,
                    updates=512, seed=202)
    # No capsule is used by the recipient at inference.
    score = world.score(predict(recipient, world.public.observations).argmax(1))
    print({"evaluation": score, "calibration": oracle.accounting(),
           "exposures": report.exposure_draws, "unique_states": report.unique_states_exposed})


if __name__ == "__main__":
    main()
