from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import Callable, Iterable, NewType, TypeVar
import parsy  # type: ignore

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


# TODO: use this instead?
Tuning = tuple[Pitch, ...]


@dataclass
class Fretboard:
    strings: Iterable[String]

    @staticmethod
    def from_tuning(tuning: str) -> Fretboard:
        """Given a string like 'E3 A4 D4 G5 B6 E6' creates a fretboard with that
        tuning. Note lowest string first"""
        return Fretboard(
            reversed(
                list(
                    String(p.to_pitch())
                    for p in musical_pitch_parser.sep_by(parsy.string(" ")).parse(
                        tuning
                    )
                )
            )
        )


T_co = TypeVar("T_co", covariant=True)


FretboardAnnotation = Callable[[tuple[StringIndex, FretIndex]], T_co | None]
# class FretboardAnnotation(Protocol[T_co]):
#     def __call__(self, loc: tuple[StringIndex, FretIndex]) -> T_co | None: ...


def _null_annotation(loc: tuple[StringIndex, FretIndex]) -> None:
    return None


StringVisitor = Callable[[Fretboard, String, StringIndex], T]
"""A callback that receives the fretboard, the string, and its index"""


def visit_fretboard(fretboard: Fretboard, visitor: StringVisitor) -> Iterable[T]:
    """Visit every string on a guitar, starting on first string, and going to the thicker strings"""

    for i, s in enumerate(fretboard.strings, 1):
        yield visitor(fretboard, s, StringIndex(i))


EADGBE = Fretboard.from_tuning("E3 A4 D4 G5 B6 E6")

# TODO: change width of fret depending how far it is

MARKED_FRETS = [1, 3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
"""Frets typically marked on a fretboard"""


def _make_fret_footer(frets: int) -> str:
    fret_set = set(filter(lambda f: f <= frets, MARKED_FRETS))

    fret_markers = (
        str(fret).ljust(2) if fret in fret_set else "  " for fret in range(1, frets + 1)
    )

    return "     " + "  ".join(fret_markers)


def render_fretboard_ascii(
    fretboard: Fretboard,
    frets: int,
    annotation: FretboardAnnotation[str] = _null_annotation,
) -> str:
    def string_visitor(
        _fretboard: Fretboard, string: String, string_index: StringIndex
    ) -> str:
        def fret_visitor(_string: String, pitch: Pitch, fret_index: FretIndex) -> str:
            if fret_index == 0:
                _, octave_pitch = pitch.to_octave()
                return str(closest_sharp(octave_pitch)).ljust(2) + " |"

            fret_annotation = annotation((string_index, fret_index)) or "-"
            return f"--{fret_annotation[0]}|"

        return "".join(visit_string(string, frets, fret_visitor))

    all_strings: Iterable[str] = visit_fretboard(fretboard, string_visitor)

    footer = _make_fret_footer(frets)

    return "\n".join(chain((*all_strings, footer)))
