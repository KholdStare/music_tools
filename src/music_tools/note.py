from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from typing_extensions import Self
from enum import Enum
from parsy import char_from, regex, seq  # type: ignore

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
__note_name_keys__: set[str] = set(map(lambda n: n.name, NoteName))


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


PitchToNote = Callable[[OctavePitch], Note]
"""A way to map from a pitch within an octave to a Note. This can be in the
context of some key"""


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
    """A pitch that is a specific note in a harmonic context (e.g. B sharp 4)"""

    note: Note
    octave: Octave

    def to_pitch(self: Self) -> Pitch:
        return Pitch(
            self.note.name.value + self.note.accidental.value + self.octave * 12
        )

    @staticmethod
    def from_pitch(
        pitch: Pitch, pitch_to_note: PitchToNote = closest_sharp
    ) -> MusicalPitch:
        octave, octave_pitch = pitch.to_octave()
        return MusicalPitch(pitch_to_note(octave_pitch), octave)

    def __repr__(self: Self) -> str:
        return f"{self.note}{self.octave}"


note_name_parser = char_from("".join(__note_name_keys__)).map(
    lambda name: NoteName[name]
)


def _chars_to_accidental(chars: list[str]) -> Accidental:
    value = 0
    for char in chars:
        if char == "b":
            value -= 1
        elif char == "#":
            value += 1
    return Accidental(value)


accidental_parser = char_from("b#").at_most(2).map(_chars_to_accidental)

note_parser = seq(note_name_parser, accidental_parser).combine(Note)

octave_parser = regex(r"[0-9]+").map(lambda i: Octave(int(i)))

musical_pitch_parser = seq(note_parser, octave_parser).combine(MusicalPitch)


def n(text: str) -> Note:
    """Shorthand to parse a note like "Bb"."""
    return note_parser.parse(text)  # type: ignore


def p(text: str) -> MusicalPitch:
    """Shorthand to parse a musical pitch like "Bb4"."""
    return musical_pitch_parser.parse(text)  # type: ignore
