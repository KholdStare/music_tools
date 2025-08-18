from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from typing_extensions import Self


Interval = NewType("Interval", int)
"""A musical interval between two pitches, in terms of half-steps (semitones)"""


@dataclass(frozen=True, init=False)
class OctavePitch:
    """Number of half-steps from C in a single octave. A pitch class as a number."""

    half_steps: int

    def __init__(self: Self, _half_steps: int):
        object.__setattr__(self, "half_steps", _half_steps % 12)

    def __add__(self: Self, interval: Interval) -> OctavePitch:
        return OctavePitch(self.half_steps + interval)

    def __sub__(self: Self, interval: Interval) -> OctavePitch:
        return OctavePitch(self.half_steps - interval)


Octave = NewType("Octave", int)
"""Which octave a particular note/pitch sits in"""


@dataclass(frozen=True)
class Pitch:
    """A pitch relative to some tuning system (e.g. A440). Defined in terms of
    half-steps away from C0 in a tuning system"""

    half_steps: int

    def __add__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps + interval)

    def __sub__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps - interval)

    @staticmethod
    def from_octave(octave: Octave, pitch: OctavePitch) -> Pitch:
        return Pitch((octave * 12) + pitch.half_steps)
