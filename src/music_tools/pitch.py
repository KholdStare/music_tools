from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from typing_extensions import Self


@dataclass(frozen=True, order=True)
class Interval:
    """A musical interval between two pitches, in terms of half-steps
    (semitones)"""

    half_steps: int

    def inside_octave(self) -> Interval:
        return Interval(self.half_steps % 12)

    def scale_degree_repr(self, degree: int) -> str:
        """Representation of interval as a scale degree. E.g. #2 vs b3"""
        distance = self.half_steps - _natural_intervals[degree % 7].half_steps
        if distance > 0:
            accidentals = distance * "♯"
        else:
            accidentals = (-distance) * "♭"
        return f"{accidentals}{degree + 1}"

    def __add__(self: Self, interval: Interval) -> Interval:
        return Interval(self.half_steps + interval.half_steps)

    def __sub__(self: Self, interval: Interval) -> Interval:
        return Interval(self.half_steps - interval.half_steps)

    def __mul__(self: Self, mult: int) -> Interval:
        return Interval(self.half_steps * mult)


@dataclass(frozen=True, init=False, order=True)
class OctavePitch:
    """Number of half-steps from C in a single octave. A pitch class as a number."""

    half_steps: int

    def __init__(self: Self, _half_steps: int):
        object.__setattr__(self, "half_steps", _half_steps % 12)

    def __add__(self: Self, interval: Interval) -> OctavePitch:
        return OctavePitch(self.half_steps + interval.half_steps)

    def __sub__(self: Self, interval: Interval) -> OctavePitch:
        return OctavePitch(self.half_steps - interval.half_steps)


Octave = NewType("Octave", int)
"""Which octave a particular note/pitch sits in"""


@dataclass(frozen=True)
class Pitch:
    """A pitch relative to some tuning system (e.g. A440). Defined in terms of
    half-steps away from C0 in a tuning system"""

    half_steps: int

    def __add__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps + interval.half_steps)

    def __sub__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps - interval.half_steps)

    @staticmethod
    def from_octave(octave: Octave, pitch: OctavePitch) -> Pitch:
        return Pitch((octave * 12) + pitch.half_steps)

    def to_octave(self: Self) -> tuple[Octave, OctavePitch]:
        octave = Octave(self.half_steps // 12)
        octave_pitch = OctavePitch(self.half_steps)
        return (octave, octave_pitch)


UNISON = Interval(0)
HALF_STEP = Interval(1)
SEMITONE = HALF_STEP
MINOR_SECOND = HALF_STEP
WHOLE_STEP = Interval(2)
MAJOR_SECOND = WHOLE_STEP
MINOR_THIRD = Interval(3)
MAJOR_THIRD = Interval(4)
FOURTH = Interval(5)
AUGMENTED_FOURTH = Interval(6)
DIMINISHED_FIFTH = AUGMENTED_FOURTH
FIFTH = Interval(7)
MINOR_SIXTH = Interval(8)
MAJOR_SIXTH = Interval(9)
DIMINISHED_SEVENTH = MAJOR_SIXTH
MINOR_SEVENTH = Interval(10)
MAJOR_SEVENTH = Interval(11)
OCTAVE = Interval(12)

_natural_intervals = (
    UNISON,
    MAJOR_SECOND,
    MAJOR_THIRD,
    FOURTH,
    FIFTH,
    MAJOR_SIXTH,
    MAJOR_SEVENTH,
)
