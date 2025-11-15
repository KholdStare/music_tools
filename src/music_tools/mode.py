from collections import OrderedDict
from collections.abc import Iterable
from math import sqrt
from typing import TypeVar
from .pitch import OCTAVE, Interval
from .scale import Scale, name_to_scale


def next_mode(scale: Scale) -> Scale:
    """Rotate intervals to form a new scale starting from the second degree"""
    new_scale = scale[1:] + (OCTAVE,)
    new_scale2 = [i - new_scale[0] for i in new_scale]
    return Scale(tuple(new_scale2))


T = TypeVar("T")


def _add_new_to_set(s: set[T], val: T) -> bool:
    didnt_exist = val not in s
    if didnt_exist:
        s.add(val)
    return didnt_exist


def scale_modes(scale: Scale) -> Iterable[Scale]:
    """Yield all unique modes of a scale"""

    mode_set: set[Scale] = set()
    while True:
        if not _add_new_to_set(mode_set, scale):
            break

        yield scale
        scale = next_mode(scale)


major_scale_modes_by_name: OrderedDict[str, Scale] = OrderedDict(
    zip(
        ("Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"),
        scale_modes(name_to_scale["Major"]),
    )
)


def scale_interval_diff(a: Scale, b: Scale) -> Iterable[tuple[int, Interval, Interval]]:
    """Return a list of differences between two scales, as tuples of the degree
    and intervals"""
    for degree, aInterval in enumerate(a):
        bInterval = b[degree]
        if aInterval != bInterval:
            yield (degree, aInterval, bInterval)


def rank_sequences_by_closeness(
    needle: list[int], haystack: list[list[int]]
) -> list[list[int]]:
    """Assume sorted!"""
    return sorted(
        haystack,
        key=lambda sequence: sum(
            map(lambda t: sqrt(abs(t[0] - t[1])), zip(needle, sequence))
        ),
        reverse=False,
    )


# TODO: convert to work with scales
