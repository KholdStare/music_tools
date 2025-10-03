from __future__ import annotations
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Mapping, NewType
from typing_extensions import Self

from .pitch import Interval
from .note import (
    Note,
    closest_sharp,
)

IntervalSequence = NewType("IntervalSequence", list[Interval])
"""A sequence of "gaps" between successive notes"""


def interval_sequence(raw_intervals: list[int]) -> IntervalSequence:
    return IntervalSequence(list(map(Interval, raw_intervals)))


Scale = NewType("Scale", tuple[Interval, ...])
"""A scale is a sequence of Intervals relative to a root pitch."""

# TODO: pick note names based on harmony


def scale_from_intervals(intervals: IntervalSequence) -> Scale:
    # TODO: ensure add up to 12 half-steps
    scale_intervals = [Interval(0)]
    for interval in intervals:
        scale_intervals.append(scale_intervals[-1] + interval)
    assert scale_intervals.pop() == Interval(12), "Intervals must span an octave"
    return Scale(tuple(scale_intervals))


name_to_scale: Mapping[str, Scale] = dict(
    (kv[0], scale_from_intervals(interval_sequence(kv[1])))
    for kv in [
        ("Major", [2, 2, 1, 2, 2, 2, 1]),
        # TODO: generate modes?
        ("Minor", [2, 1, 2, 2, 1, 2, 2]),
        ("Harmonic Minor", [2, 1, 2, 2, 1, 3, 1]),
        ("Melodic Minor", [2, 1, 2, 2, 2, 2, 1]),
        ("Harmonic Major", [2, 2, 1, 2, 1, 3, 1]),
        ("Whole-Tone", [2, 2, 2, 2, 2, 2]),
        ("Whole-Half Diminished", [2, 1, 2, 1, 2, 1, 2, 1]),
        ("Augmented", [3, 1, 3, 1, 3, 1]),
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
        return scale_from_intervals(interval_sequence(self.interval_sequence))


# TODO: write tests
# TODO: re-write using generator rules

# Insight! Any two adjacent intervals must add up to minor or major third (3 or 4 half-steps)
possible_transitions: Mapping[int, list[list[int]]] = {
    1: [[2], [3]],
    2: [[1], [2]],
    3: [[1]],
}


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
