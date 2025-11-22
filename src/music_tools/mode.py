from collections import OrderedDict
from collections.abc import Iterable
from typing import TypeVar, cast

from music_tools.algorithms import (
    Edits,
    LevenshteinEditMatrix,
    rank_sequences_by_closeness,
)
from .pitch import OCTAVE, Interval
from .scale import Scale, name_to_scale, _interval_cost


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


def rank_scales_by_closeness(
    scale: Scale, candidates: Iterable[Scale]
) -> list[tuple[Scale, Edits[Interval]]]:
    # Cast is necessary because can't express this properly in type system
    # See https://github.com/python/mypy/issues/20293
    return cast(
        list[tuple[Scale, Edits[Interval]]],
        rank_sequences_by_closeness(scale, candidates, _interval_cost),
    )
