from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, NewType, TypeVar
from parsy import string  # type: ignore

from music_tools.note import (
    closest_sharp,
    musical_pitch_parser,
)
from music_tools.pitch import HALF_STEP, Pitch


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

    @staticmethod
    def from_tuning(tuning: str) -> Fretboard:
        """Given a string like 'E3 A4 D4 G5 B6 E6' creates a fretboard with that
        tuning. Note lowest string first"""
        return Fretboard(
            reversed(
                list(
                    String(p.to_pitch())
                    for p in musical_pitch_parser.sep_by(string(" ")).parse(tuning)
                )
            )
        )


StringVisitor = Callable[[Fretboard, String, StringIndex], T]
"""A callback that receives the fretboard, the string, and its index"""


def visit_fretboard(fretboard: Fretboard, visitor: StringVisitor) -> Iterable[T]:
    """Visit every string on a guitar, starting on first string, and going to the thicker strings"""

    for i, s in enumerate(fretboard.strings, 1):
        yield visitor(fretboard, s, StringIndex(i))


EADGBE = Fretboard.from_tuning("E3 A4 D4 G5 B6 E6")

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
