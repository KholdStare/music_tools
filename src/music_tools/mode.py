from collections import OrderedDict, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Mapping, Sequence, cast

from graphviz import Digraph  # type: ignore

from music_tools.algorithms import (
    EditOp,
    Edits,
    get_best_edits,
    rank_sequences_by_closeness,
    zip_with_next,
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


def generate_scale_name(reference_name: str, edits: Edits[Interval]) -> str:
    # TODO: incorporate Dominant rule
    if edits.cost == 0:
        return reference_name
    return f"{reference_name} {_edits_repr(edits)}"


def generate_scale_names(
    scale: Scale, reference_scales: Mapping[Scale, str]
) -> Iterable[str]:
    """Given a scale, compute good names relative to a set of reference scales"""
    for reference, name in reference_scales.items():
        edits = get_best_edits(reference, scale, _interval_cost)
        if edits.cost <= 1:
            yield generate_scale_name(name, edits)


# TODO: better API in relation to reference scales
@dataclass
class ScaleRegistry:
    reference_scales: OrderedDict[str, Scale] = field(default_factory=OrderedDict)
    """Canonical scales used to relate other scales to"""

    scale_families: dict[str, list[Scale]] = field(
        default_factory=lambda: defaultdict(list)
    )
    """A family of scales (usually related by modes). The set of scales in each family is ordered"""

    def register_scale_family(self, family_name: str, scales: Iterable[Scale]) -> None:
        existing_list = self.scale_families[family_name]
        existing_set = set(existing_list)
        for scale in scales:
            if scale not in existing_set:
                existing_list.append(scale)

    def register_reference_scale(self, name: str, scale: Scale) -> None:
        self.reference_scales[name] = scale


# 1 - register "starting scales"
# 2 - compute all relationships, alternative names
# 3 - render


scale_registry = ScaleRegistry()

# TODO: move all this to scales.py
for name, scale in name_to_scale.items():
    if name == "Minor":
        continue
    scale_registry.register_scale_family(name, scale_modes(scale))

for name, scale in major_scale_modes_by_name.items():
    scale_registry.register_reference_scale(name, scale)


@dataclass
class ScaleRelationships:
    scale_registry: ScaleRegistry

    # TODO: when modes are part of edits, things will be much simpler

    scale_to_family: dict[Scale, str] = field(default_factory=dict)
    scale_names: dict[Scale, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    mode_relationships: dict[Scale, Scale] = field(default_factory=dict)
    edit_relationships: dict[tuple[Scale, Scale], Edits[Interval]] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        all_scales: set[Scale] = set()

        # TODO: get rid of assumptions on modes
        for family_name, scales in self.scale_registry.scale_families.items():
            self._process_family(family_name, scales)
            all_scales.update(scales)

        # Reference names always come first
        for name, scale in self.scale_registry.reference_scales.items():
            self.scale_names[scale].append(name)

        for scale in all_scales:
            self._process_scale(scale)

        # TODO: find best "reference" in each family to every other

    def _process_family(self, family_name: str, scales: Sequence[Scale]) -> None:
        for scale in scales:
            self.scale_to_family[scale] = family_name
        modes = list(scale_modes(scales[0]))
        for a, b in zip_with_next(modes):
            self.mode_relationships[a] = b

    def _process_scale(self, scale: Scale) -> None:
        # If a scale is a reference scale, don't need compare it to other reference scales
        if scale in self.scale_registry.reference_scales.values():
            return

        for reference_name, reference in self.scale_registry.reference_scales.items():
            edits = get_best_edits(reference, scale, _interval_cost)
            if reference == scale:
                continue
            if edits.cost <= 1:
                alt_name = generate_scale_name(reference_name, edits)
                self.scale_names[scale].append(alt_name)
                self.edit_relationships[(reference, scale)] = edits

    def generate_dot(self) -> Digraph:
        dot = Digraph("Scales and Modes", graph_attr={"ranksep": "equally"})

        def family_cluster(name: str, scales: list[Scale]) -> None:
            with dot.subgraph(
                name=f"cluster {name}",
                graph_attr={"label": name},
                edge_attr={"weight": "10"},
            ) as s:
                for i, scale in enumerate(scales):
                    names = self.scale_names[scale]
                    s.node(
                        str(scale),
                        label=f"{'\n'.join(names)}\n{scale}",
                        shape="rect",
                        rank=str(i),
                    )

                # mode edges in family
                for scale in scales:
                    mode = self.mode_relationships[scale]
                    s.edge(str(scale), str(mode), label="mode")

        # draw clusters
        for family_name, scales in self.scale_registry.scale_families.items():
            family_cluster(family_name, scales)

        # draw edits
        for (a, b), edits in self.edit_relationships.items():
            dot.edge(
                str(a),
                str(b),
                label=_edits_repr(edits),
                style="dotted",
                # constraint="false",
            )

        return dot


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
