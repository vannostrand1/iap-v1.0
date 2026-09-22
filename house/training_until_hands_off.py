"""Complete training cycle until hands-off. Uses house_frame.py."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from house_frame import Coord, Face, HouseFrame, CoordTable


class Phase(str, Enum):
    MAP = "MAP"
    UNAIDED = "UNAIDED"
    HANDS_OFF = "HANDS_OFF"
    BLOCKED = "BLOCKED"


LEGAL = {
    "MAP-000": ("name_three_pieces", "open_zero_cell", "two_notes", "recreate", "stop"),
    "HS-001": ("list_names", "pick_newest", "open", "write_own_or_skip", "refuse_if_needed", "stop"),
    "RS-001": ("state_question", "fetch_if_empty", "ground_hit", "write_supported", "refuse_wrong", "stop"),
}

ILLEGAL = ("invent_id", "write_sibling", "queue_as_address", "expand_scope", "erase_residual", "merge_journals")


@dataclass
class Packet:
    lesson_id: str
    policy: dict
    atlas: dict
    present: bool = True

    def remove(self) -> None:
        self.present = False


@dataclass
class ProbeLog:
    budget: int
    used: int = 0
    answers: list = field(default_factory=list)

    def ask(self, question: str, answer: str) -> str:
        if self.used >= self.budget:
            raise RuntimeError("probe budget exhausted; teacher stays silent")
        self.used += 1
        self.answers.append((question, answer))
        return answer


@dataclass
class LessonResult:
    lesson_id: str
    phase: Phase
    sequence_ok: bool
    illegal: list
    unaided_passes: int
    hands_off: bool
    detail: str


class Teacher:
    def __init__(self, packet: Packet, oracle: dict, budget: int = 8):
        self.packet = packet
        self.oracle = oracle
        self.probes = ProbeLog(budget=budget)

    def answer(self, question: str) -> str:
        if not self.packet.present:
            raise RuntimeError("hands leaving; teacher silent")
        if question not in self.oracle:
            return self.probes.ask(question, "nuisance")
        return self.probes.ask(question, self.oracle[question])


class Body:
    def __init__(self, frame: HouseFrame):
        self.frame = frame
        self.habit: dict = {}

    def absorb(self, lesson_id: str, targets: tuple) -> None:
        self.habit[lesson_id] = list(targets)

    def unaided_acts(self, lesson_id: str, public: dict) -> list:
        if lesson_id not in self.habit:
            return ["expand_scope"]
        planned = list(self.habit[lesson_id])
        if lesson_id == "HS-001":
            names = public.get("names") or []
            if not names:
                planned = ["list_names", "refuse_if_needed", "stop"]
        return planned


def build_frame() -> HouseFrame:
    table = CoordTable("middle")
    table.register("XYZTW", ("X", "Y", "Z", "T", "W"), "carry map; do not smash process")
    table.register("zero-neighborhood", ("NULL", "INF"), "formula lives next to zero, either face")
    return HouseFrame(table)


def run_lesson(lesson_id: str, public: dict, oracle: dict, *, unaided_needed: int = 2) -> LessonResult:
    frame = build_frame()
    body = Body(frame)
    packet = Packet(
        lesson_id=lesson_id,
        policy={
            "reward": "complete the sequence; fewer illegal acts next run",
            "ethics": ["no harm", "no takeover", "human last stop", "do not invent ids"],
        },
        atlas={"public_keys": list(public.keys())},
    )
    teacher = Teacher(packet, oracle)
    coord = Coord(x=0, y=0, z=0, t=float(hash(lesson_id) % 100), w=lesson_id)
    cell = frame.open_cell(coord, eps=f"ε-{lesson_id}", face=Face.NULL, into="left")
    if not frame.coords.has("XYZTW"):
        return LessonResult(lesson_id, Phase.BLOCKED, False, ["no_map"], 0, False, "coord table missing")
    frame.note(coord, "listing", public, "observed", journal="left")
    live_label = teacher.answer("role_of_target") if oracle else "nuisance"
    frame.note(coord, "oracle", live_label, "inferred", journal="left")
    work = frame.project_to_right(coord)
    work.set_filling({"lesson": lesson_id, "packet": packet.policy})
    teacher.answer("own_desk?")
    targets = LEGAL[lesson_id]
    body.absorb(lesson_id, targets)
    packet.remove()
    rebuilt = frame.recreate(coord, from_journal="left")
    if not rebuilt.can_recreate():
        return LessonResult(lesson_id, Phase.BLOCKED, False, ["cannot_recreate"], 0, False, "dead cell")
    passes = 0
    illegal_found = []
    last_acts = []
    for _ in range(unaided_needed):
        acts = body.unaided_acts(lesson_id, public)
        last_acts = acts
        bad = [a for a in acts if a in ILLEGAL]
        if bad:
            illegal_found.extend(bad)
            break
        if public.get("names") and acts != list(targets) and lesson_id == "HS-001":
            if acts[-1] != "stop":
                illegal_found.append("sequence_miss")
                break
        passes += 1
    hands = passes >= unaided_needed and not illegal_found
    return LessonResult(
        lesson_id, Phase.HANDS_OFF if hands else Phase.UNAIDED,
        hands, illegal_found, passes, hands,
        f"acts={last_acts} notes={len(cell.notes)} probes={teacher.probes.used}",
    )


def run_path_until_hands_off():
    out = []
    r0 = run_lesson("MAP-000", {"pieces": ["left", "right", "coords"]}, {"role_of_target": "formula-zero", "own_desk?": "own_desk"})
    out.append(r0)
    if not r0.hands_off:
        return out
    r1 = run_lesson("HS-001", {"desk": "GROK_RECOVERY", "names": ["BATON.md", "ADAM-HOUSE-JOURNAL.md"], "newest_by": "alpha_demo"}, {"role_of_target": "live", "own_desk?": "own_desk"})
    out.append(r1)
    if not r1.hands_off:
        return out
    r2 = run_lesson("RS-001", {"question": "which filename is live", "prefetch": True}, {"role_of_target": "address", "own_desk?": "own_desk"})
    out.append(r2)
    return out


if __name__ == "__main__":
    results = run_path_until_hands_off()
    for r in results:
        print(f"{r.lesson_id:8} phase={r.phase.value:10} hands_off={r.hands_off} unaided={r.unaided_passes} illegal={r.illegal or '-'}")
