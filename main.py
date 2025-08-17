from dataclasses import dataclass
from typing import NewType, TypeAlias
from typing_extensions import Self

from enum import Enum

class NoteName(Enum):
    C = 0
    D = 2
    E = 4
    F = 5
    G = 7
    A = 9
    B = 11

class Accidental(Enum):
    DoubleFlat = -2
    Flat = -1
    Natural = 0
    Sharp = 1
    DoubleSharp = 2

@dataclass
class Note:
    name: NoteName
    accidental: Accidental

    def __str__(self: Self) -> str:
        if self.accidental.value > 0:
            accidentals = self.accidental.value * "#"
        else:
            accidentals = self.accidental.value * "b"
        return f"{self.name.name}{accidentals}"

Octave: TypeAlias = NewType("Octave", int)
"""Which octave a particular note sits in"""

Pitch: TypeAlias = NewType("Pitch", int)
"""A pitch relative to some tuning system (e.g. A440). Defined in terms of
half-steps away from C0 in a tuning system"""

@dataclass
class MusicalPitch:
    """A pitch that is a specific note in a harmonic context (e.g. B sharp)"""
    note: Note
    octave: Octave

    def to_pitch(self: Self) -> Pitch:
        return self.note.name + self.note.accidental + self.octave * 12

    def __str__(self: Self) -> str:
        return f"{self.note}{self.octave}"


def main():
    a4 = MusicalPitch(Note(NoteName.A, Accidental.Natural), Octave(4))
    print(a4)


if __name__ == "__main__":
    main()
