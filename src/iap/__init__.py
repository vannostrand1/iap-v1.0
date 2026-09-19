"""IAP: bounded, architecture-neutral behavioral transfer.

Importing IAP does not load a teacher, enumerate hypotheses, or change global
random seeds / Torch thread settings. Training backends are imported on demand.
"""
from .packets import CultureCapsule, PolicyPacket, PacketError

__version__ = "1.0.0"
__all__ = ["CultureCapsule", "PolicyPacket", "PacketError", "__version__"]
