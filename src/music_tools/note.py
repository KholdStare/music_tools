from __future__ import annotations
from dataclasses import dataclass, field
from typing_extensions import Self
from enum import Enum

from .pitch import Pitch, OctavePitch, Octave


class NoteName(Enum):
    """Western pitch class names"""

    C = 0
    D = 2
    E = 4
    F = 5
    G = 7
    A = 9
    B = 11


__note_name_values__: set[int] = set(map(lambda n: n.value, NoteName))


class Accidental(Enum):
    DoubleFlat = -2
    Flat = -1
    Natural = 0
    Sharp = 1
    DoubleSharp = 2


@dataclass
class Note:
    """A named pitch class - a note regardless of its octave"""

    name: NoteName
    accidental: Accidental = field(default=Accidental.Natural)

    def to_octave_pitch(self: Self) -> OctavePitch:
        """Number of half-steps above C"""
        return OctavePitch(self.name.value + self.accidental.value)

    def __repr__(self: Self) -> str:
        if self.accidental.value > 0:
            accidentals = self.accidental.value * "#"
        else:
            accidentals = (-self.accidental.value) * "b"
        return f"{self.name.name}{accidentals}"


def closest_sharp(octave_pitch: OctavePitch) -> Note:
    if octave_pitch.half_steps in __note_name_values__:
        return Note(NoteName(octave_pitch.half_steps), Accidental.Natural)
    else:
        return Note(NoteName(octave_pitch.half_steps - 1), Accidental.Sharp)


def closest_flat(octave_pitch: OctavePitch) -> Note:
    if octave_pitch.half_steps in __note_name_values__:
        return Note(NoteName(octave_pitch.half_steps), Accidental.Natural)
    else:
        return Note(NoteName(octave_pitch.half_steps + 1), Accidental.Flat)


sharp_notes = tuple(map(closest_sharp, map(OctavePitch, range(0, 12))))
flat_notes = tuple(map(closest_flat, map(OctavePitch, range(0, 12))))


@dataclass
class MusicalPitch:
    """A pitch that is a specific note in a harmonic context (e.g. B sharp)"""

    note: Note
    octave: Octave

    def to_pitch(self: Self) -> Pitch:
        return Pitch(
            self.note.name.value + self.note.accidental.value + self.octave * 12
        )

    def __repr__(self: Self) -> str:
        return f"{self.note}{self.octave}"


# TODO: harmonic pitch?
