import torch
import pytest
from pathlib import Path


@pytest.fixture(autouse=True, scope="session")
def cpu_threads():
    old = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(old)


@pytest.fixture(scope="session")
def repository():
    return Path(__file__).resolve().parents[1]
