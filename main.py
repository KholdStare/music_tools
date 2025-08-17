from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Mapping, NewType
from typing_extensions import Self
from itertools import chain
from enum import Enum


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
"""Which octave a particular note sits in"""


@dataclass(frozen=True)
class Pitch:
    """A pitch relative to some tuning system (e.g. A440). Defined in terms of
    half-steps away from C0 in a tuning system"""

    half_steps: int

    def __add__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps + interval)

    def __sub__(self: Self, interval: Interval) -> Pitch:
        return Pitch(self.half_steps - interval)


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

IntervalSequence = NewType("IntervalSequence", tuple[Interval, ...])
"""A sequence of "gaps" between successive notes"""


def interval_sequence(raw_intervals: list[int]) -> IntervalSequence:
    return IntervalSequence(tuple(map(Interval, raw_intervals)))


Scale = NewType("Scale", tuple[Interval, ...])
"""A scale is a sequence of Intervals relative to a root pitch."""

# TODO: pick note names based on harmony


def scale_from_intervals(intervals: IntervalSequence) -> Scale:
    scale_intervals = [Interval(0)]
    for interval in intervals:
        scale_intervals.append(Interval(scale_intervals[-1] + interval))
    return Scale(tuple(scale_intervals))


name_to_scale: Mapping[str, Scale] = dict(
    (kv[0], scale_from_intervals(interval_sequence(kv[1])))
    for kv in [
        ("Major", [2, 2, 1, 2, 2, 2]),
        # TODO: generate modes?
        ("Minor", [2, 1, 2, 2, 1, 2]),
        ("Harmonic Minor", [2, 1, 2, 2, 1, 3]),
        ("Melodic Minor", [2, 1, 2, 2, 2, 2]),
        ("Harmonic Major", [2, 2, 1, 2, 1, 3]),
        ("Whole-Tone", [2, 2, 2, 2, 2]),
        ("Whole-Half Diminished", [2, 1, 2, 1, 2, 1, 2]),
        ("Augmented", [3, 1, 3, 1, 3]),
    ]
)
scale_to_name: Mapping[Scale, str] = dict(
    (kv[1], kv[0]) for kv in name_to_scale.items()
)

# TODO: better name?
ConcreteScale = NewType("ConcreteScale", tuple[Note, ...])
"""A Scale starting from a particular root note"""


def scale_with_root(note: Note, scale: Scale) -> ConcreteScale:
    start = note.to_octave_pitch()
    half_steps = map(lambda interval: start + interval, scale)
    # TODO: this is not correct in general. Need "key signature"
    # where no note name repeats
    return ConcreteScale(tuple(map(closest_sharp, half_steps)))


@dataclass(frozen=True)
class _ScaleFragment:
    interval_sequence: list[int]
    sum: int

    def to_scale(self: Self) -> Scale:
        return scale_from_intervals(interval_sequence(self.interval_sequence[:-1]))


def gen_scale_fragment_extensions(fragment: _ScaleFragment) -> Iterable[_ScaleFragment]:
    """Given a scale fragment, generate a new set of extended scale fragments
    that are at most an octave"""
    last_interval = fragment.interval_sequence[-1] if fragment.interval_sequence else 0
    match last_interval:
        case 0:
            intervals_to_try = [1, 2, 3]
        case 1:
            intervals_to_try = [2, 3]
        case 2:
            intervals_to_try = [1, 2]
        case 3:
            intervals_to_try = [1]

    for interval in intervals_to_try:
        new_fragment = _ScaleFragment(
            fragment.interval_sequence + [interval],
            fragment.sum + interval,
        )
        first_and_last_compatible = not (
            (new_fragment.interval_sequence[0] == 1 and interval != 2)
            or (new_fragment.interval_sequence[0] == 3 and interval != 1)
        )
        if new_fragment.sum < 12:
            yield new_fragment
        elif new_fragment.sum == 12 and first_and_last_compatible:
            yield new_fragment


def gen_conventional_scales() -> Iterable[Scale]:
    current_fragments: list[_ScaleFragment] = [_ScaleFragment([], 0)]

    while len(current_fragments):
        completed_fragments = filter(lambda f: f.sum == 12, current_fragments)
        yield from map(_ScaleFragment.to_scale, completed_fragments)
        current_fragments = list(
            chain(*map(gen_scale_fragment_extensions, current_fragments))
        )


# TODO: categorize each generated scale as mode of some parent scale


def main():
    a4 = MusicalPitch(Note(NoteName.A, Accidental.Natural), Octave(4))
    print(a4)
    print(sharp_notes)
    print(flat_notes)
    print(name_to_scale["Major"])
    for note in sharp_notes:
        print(f"{note} major", scale_with_root(note, name_to_scale["Major"]))

    all_scales = list(gen_conventional_scales())
    print(len(all_scales))
    for scale in all_scales:
        print(scale_with_root(Note(NoteName.C), scale))


if __name__ == "__main__":
    main()
