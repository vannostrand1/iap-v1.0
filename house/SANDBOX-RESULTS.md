# Sandbox measurements 2026-09-22

Environment: Python 3.12.3, torch 2.12+cpu, IAP v1.0.0 doctor 13 assets.

## Their protocol (not house curriculum)

pytest: 49 passed

ground-only:
- transformer/ontology action=1.0 sequence=1.0
- mlp/permutation action=1.0 sequence=0.0
- mlp/relational action=1.0 sequence=0.0

Fly → Transformer, updates=512, seed=1300000, queries=8, lr=0.05:

| condition | action | sequence |
| grounded_culture | 1.00 | 1.00 |
| query_only_no_packet | 0.69 | 0.00 |
| ungrounded_identity | 0.23 | 0.00 |

Smoke (64 updates) did not reach sequence success. Use 512 for their replay.

## House meaning of that table

Packet + bounded grounding is the piece we keep.
World (Fly/Transformer/Doom) is lineage, not the Studio lesson.
