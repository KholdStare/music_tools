# minor, major, suspended, augmented, diminished
#
# major 7 - Δ
# ° ∅
# ♭ ♯ ♮

from dataclasses import dataclass
from enum import Enum
from typing import NewType

from music_tools.note import Note
from music_tools.scale import Scale

from .pitch import OctavePitch


class ToneQuality(Enum):
    Diminished = -2
    Minor = -1
    Major = 0
    Augmented = 1


class Extension(Enum):
    """Chord triad extension"""

    MinorSix = 8
    Six = 9
    DiminishedSeven = 9
    MinorSeven = 10
    MajorSeven = 11


class Tension(Enum):
    """Chord tensions"""

    FlatNine = 1  # ♭9
    Nine = 2  # ♮9
    SharpNine = 3  # ♯9
    Eleven = 5  # ♮11
    SharpEleven = 6  # ♯11
    FlatThirteen = 8  # ♭13
    Thirteen = 9  # ♮13


@dataclass
class ChordDescription:
    triad: ToneQuality
    # TODO: suspensions
    extension: Extension
    tensions: list[Tension]


ChordScale = Scale
"""Raw set of intervals that define a type of chord"""

Chord = NewType("Chord", tuple[OctavePitch, ...])

# TODO: go from chord intervals to a description, e.g. m7b5


def instantiate_chord(chord_scale: ChordScale, root: Note) -> Chord:
    root_pitch = root.to_octave_pitch()
    return Chord(tuple((root_pitch + interval for interval in chord_scale)))


# TODO: overload for concrete scale
def triads_in_scale(
    scale: Scale, *, include_seven: bool = False
) -> list[tuple[int, ChordScale]]:
    pass
    # for (i, interval)
