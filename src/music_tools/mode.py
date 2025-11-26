from collections import OrderedDict, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Mapping, cast

from music_tools.algorithms import (
    EditOp,
    Edits,
    get_best_edits,
    rank_sequences_by_closeness,
)
from .pitch import OCTAVE, Interval
from .scale import Scale, name_to_scale, _interval_cost


def next_mode(scale: Scale) -> Scale:
    """Rotate intervals to form a new scale starting from the second degree"""
    new_scale = scale[1:] + (OCTAVE,)
    new_scale2 = [i - new_scale[0] for i in new_scale]
    return Scale(tuple(new_scale2))


def _add_new_to_set[T](s: set[T], val: T) -> bool:
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


def _edits_repr(edits: Edits[Interval]) -> str:
    """Representation of edits in context of scale intervals"""

    def edit_repr(edit: EditOp[Interval]) -> str:
        interval = edit.right_value or edit.left_value
        assert interval is not None, (
            "Can't have an edit with both left/right values missing"
        )

        if edit.right_value is None:
            insert_remove = "-"
        elif edit.left_value is None:
            insert_remove = "+"
        else:
            insert_remove = ""

        interval_repr = interval.scale_degree_repr(
            edit.left_position, include_natural=True
        )
        return insert_remove + interval_repr

    return " ".join(map(edit_repr, edits.edits))


def generate_scale_names(
    scale: Scale, reference_scales: Mapping[Scale, str]
) -> Iterable[str]:
    """Given a scale, compute good names relative to a set of reference scales"""
    for reference, name in reference_scales.items():
        edits = get_best_edits(reference, scale, _interval_cost)
        if edits.cost == 0:
            yield name
        if edits.cost <= 1:
            yield f"{name} {_edits_repr(edits)}"


@dataclass
class ScaleRegistry:
    scale_by_name: dict[str, Scale] = field(default_factory=dict)
    names_by_scale: dict[Scale, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    reference_scales: OrderedDict[Scale, str] = field(default_factory=OrderedDict)
    """Scales used to related other scales to"""

    def register_scale(
        self, name: str, scale: Scale, *, is_reference: bool = False
    ) -> None:
        self.scale_by_name[name] = scale
        names = self.names_by_scale[scale]
        if name not in names:
            names.append(name)

        if is_reference:
            self.reference_scales[scale] = name


scale_registry = ScaleRegistry()

for name, scale in name_to_scale.items():
    scale_registry.register_scale(name, scale)

for name, scale in major_scale_modes_by_name.items():
    scale_registry.register_scale(name, scale, is_reference=True)


class ScaleRelationships:
    scale_registry: ScaleRegistry
    mode_relationships: set[tuple[Scale, Scale]]


# TODO: generate names for other modes relative to major modes


def rank_scales_by_closeness(
    scale: Scale, candidates: Iterable[Scale]
) -> list[tuple[Scale, Edits[Interval]]]:
    # Cast is necessary because can't express this properly in type system
    # See https://github.com/python/mypy/issues/20293
    return cast(
        list[tuple[Scale, Edits[Interval]]],
        rank_sequences_by_closeness(scale, candidates, _interval_cost),
    )
