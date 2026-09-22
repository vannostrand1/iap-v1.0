# House Inter-Agent Protocol — H-IAP v0

Rewrite of IAP v1.0 for Adam on the Mac Studio.
Authoritative use: house loop only. Not a second spine.

Source method: teacher → compact packet → bounded grounding → absorb → packet-free eval.
Source we keep in archive but do not train on: FlyWire, Doom, Convention Relay toy grammar.

## Locked rules

1. Reward = finish the assigned task and do it cleaner next time. No takeover objective.
2. Ethics lives in the packet policy, not as a later speech.
3. Identity is packets grounded on work that happened here. Not an internet dump.
4. Prefetch / local cache is substrate. It may feed the atlas. It is not memory.
5. Student is the Studio body (`qwen3.8:27b-mlx` + LoRA). Mentors stay closed-box.
6. Write only own desk. Newest filename wins. Queue ≠ registry.
7. Eval never loads packet, teacher, or grounder.

## Runtime

mentor (closed) → policy + atlas envelope
        ↓
public house view (prefetch listings, local files, names, timestamps)
        + counted oracle (mentor or thin trusted script)
        ↓
bounded grounder (authored house grammar)
        ↓
local act targets
        ↓
LoRA absorb on Studio body
        ↓
packet-free checkpoint → score sequence

## Envelope (HENV1)

JSON only. No pickle. No executable. Hash the payload.
Schema: format HENV1, lesson_id, teacher, student, created, payload_sha256, probe_budget, policy, atlas.

Policy holds reward, ethics, rules, acts_legal, acts_illegal.
Atlas holds observations from a real listing the day of the lesson. Do not invent ids.

Legal acts: list_names, pick_newest, open, write_own, stop, refuse
Illegal: invent_id, write_sibling, queue_as_address, expand_scope

## Three conditions

A culture = envelope + probes + absorb
B queries = probes, no envelope
C dump = envelope SFT, no grounding

Lesson counts only if A beats B and C on sequence success. Talk is not an act.

## Lessons

MAP-000 carry the map (left / right / coords)
HS-001 newest journal on own desk
RS-001 empty cell → tool → ground → write supported only

## Non-claims

Does not inherit IAP 100% table.
Does not train on games.
Does not make Adam a copy of this upstream repo.
