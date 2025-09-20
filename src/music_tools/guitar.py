from dataclasses import dataclass
from typing import Callable, Iterable, NewType, TypeVar

from music_tools.note import MusicalPitch, Note, NoteName, closest_sharp
from music_tools.pitch import HALF_STEP, Octave, Pitch


@dataclass
class String:
    open_pitch: Pitch


FretIndex = NewType("FretIndex", int)
"""Fret index on a string. 0 means open string, 1 first fret, and so on"""

T = TypeVar("T")

FretVisitor = Callable[[String, Pitch, FretIndex], T]
"""A callback that receives string, the pitch of a fret, and its index"""


def visit_string(string: String, frets: int, visitor: FretVisitor[T]) -> Iterable[T]:
    """Visit every fret on a string, starting on open string, inclusive of last fret"""
    current_pitch = string.open_pitch
    for fret in range(0, frets + 1):
        yield visitor(string, current_pitch, FretIndex(fret))
        current_pitch += HALF_STEP


StringIndex = NewType("StringIndex", int)
"""String index on a guitar. 1-based, where 1 is the first (thinnest) string and so on"""


@dataclass
class Fretboard:
    strings: list[String]


StringVisitor = Callable[[Fretboard, String, StringIndex], T]
"""A callback that receives the fretboard, the string, and its index"""


def visit_fretboard(fretboard: Fretboard, visitor: StringVisitor) -> Iterable[T]:
    """Visit every string on a guitar, starting on first string, and going to the thicker strings"""

    for i, string in enumerate(fretboard.strings, 1):
        yield visitor(fretboard, string, StringIndex(i))


# TODO: create fretboard from tuning
# TODO: parse from string

EADGBE = Fretboard(
    [
        String(MusicalPitch(Note(NoteName.E), Octave(6)).to_pitch()),
        String(MusicalPitch(Note(NoteName.B), Octave(6)).to_pitch()),
        String(MusicalPitch(Note(NoteName.G), Octave(5)).to_pitch()),
        String(MusicalPitch(Note(NoteName.D), Octave(4)).to_pitch()),
        String(MusicalPitch(Note(NoteName.A), Octave(4)).to_pitch()),
        String(MusicalPitch(Note(NoteName.E), Octave(3)).to_pitch()),
    ]
)

# TODO: change width of fret depending how far it is


def fretboard_to_ascii(fretboard: Fretboard, frets: int) -> str:
    def fret_visitor(_string: String, pitch: Pitch, index: FretIndex) -> str:
        if index == 0:
            _, octave_pitch = pitch.to_octave()
            return str(closest_sharp(octave_pitch)) + " |"
        else:
            return "---|"

    def string_visitor(
        _fretboard: Fretboard, string: String, _index: StringIndex
    ) -> str:
        return "".join(visit_string(string, frets, fret_visitor))

    return "\n".join(visit_fretboard(fretboard, string_visitor))
