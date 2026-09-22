"""
House frame: two journals + carried coordinate table.

Left  = all available space
Right = one working subset (a filling)
Middle = coordinate systems carried through both

Third person: a note per perspective inside the frame.
A formula lives in the neighborhood of zero (NULL face or INF face).
Carry residual + coordinates -> recreate the point unless the remainder was erased.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Face(str, Enum):
    NULL = "NULL"
    INF = "INF"


class Status(str, Enum):
    LIVE = "LIVE"
    ERASED = "ERASED"


@dataclass(frozen=True)
class Coord:
    """A point address. Values may be None when the axis is unused."""

    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    t: Optional[float] = None
    w: Optional[str] = None

    def key(self) -> tuple:
        return (self.x, self.y, self.z, self.t, self.w)


@dataclass
class Residual:
    """First-class remainder. If this is gone, the point cannot be rebuilt."""

    eps: Any
    face: Face
    erased: bool = False

    def wipe(self) -> None:
        self.erased = True
        self.eps = None


@dataclass
class PerspectiveNote:
    perspective: str
    seen: Any
    provenance: str


@dataclass
class Cell:
    coord: Coord
    residual: Residual
    filling: Any = None
    notes: list = field(default_factory=list)
    status: Status = Status.LIVE

    def add_note(self, perspective: str, seen: Any, provenance: str) -> None:
        self.notes.append(PerspectiveNote(perspective, seen, provenance))

    def set_filling(self, value: Any) -> None:
        if self.status is Status.ERASED or self.residual.erased:
            raise RuntimeError("cannot fill an erased remainder")
        self.filling = value

    def erase_remainder(self) -> None:
        self.residual.wipe()
        self.filling = None
        self.status = Status.ERASED

    def can_recreate(self) -> bool:
        return self.status is Status.LIVE and not self.residual.erased


class CoordTable:
    def __init__(self, name: str):
        self.name = name
        self.systems: dict[str, dict[str, Any]] = {}

    def register(self, system_id: str, axes: tuple[str, ...], rule: str) -> None:
        self.systems[system_id] = {"axes": axes, "rule": rule}

    def has(self, system_id: str) -> bool:
        return system_id in self.systems


class Journal:
    def __init__(self, name: str):
        self.name = name
        self.cells: dict[tuple, Cell] = {}

    def put(self, cell: Cell) -> None:
        self.cells[cell.coord.key()] = cell

    def get(self, coord: Coord) -> Optional[Cell]:
        return self.cells.get(coord.key())

    def live(self) -> list:
        return [c for c in self.cells.values() if c.can_recreate()]


class HouseFrame:
    def __init__(self, coord_table: CoordTable):
        self.left = Journal("available-space")
        self.right = Journal("working-subset")
        self.coords = coord_table

    def open_cell(self, coord: Coord, eps: Any, face: Face, *, into: str = "left", filling: Any = None) -> Cell:
        cell = Cell(coord=coord, residual=Residual(eps=eps, face=face), filling=filling)
        journal = self.left if into == "left" else self.right
        journal.put(cell)
        return cell

    def project_to_right(self, coord: Coord) -> Cell:
        src = self.left.get(coord)
        if src is None:
            raise KeyError("no such point on the left")
        if not src.can_recreate():
            raise RuntimeError("remainder erased; cannot project")
        dst = Cell(
            coord=src.coord,
            residual=Residual(eps=src.residual.eps, face=src.residual.face),
            filling=src.filling,
            notes=list(src.notes),
        )
        self.right.put(dst)
        return dst

    def recreate(self, coord: Coord, *, from_journal: str = "left") -> Cell:
        journal = self.left if from_journal == "left" else self.right
        cell = journal.get(coord)
        if cell is None:
            raise KeyError("no coordinates for that point")
        if not cell.can_recreate():
            raise RuntimeError("remainder erased; path back is gone")
        return Cell(
            coord=cell.coord,
            residual=Residual(eps=cell.residual.eps, face=cell.residual.face),
            filling=cell.filling,
            notes=list(cell.notes),
        )

    def note(self, coord: Coord, perspective: str, seen: Any, provenance: str, *, journal: str = "right") -> None:
        book = self.left if journal == "left" else self.right
        cell = book.get(coord)
        if cell is None:
            raise KeyError("no cell for that coordinate")
        cell.add_note(perspective, seen, provenance)
