from itertools import starmap
from music_tools.algorithms import EditOp, Edits
from music_tools.mode import (
    _edits_repr,
    next_mode,
    scale_modes,
    major_scale_modes_by_name,
)
from music_tools.note import n
from music_tools.pitch import (
    MAJOR_SECOND,
    MAJOR_SEVENTH,
    MAJOR_SIXTH,
    MAJOR_THIRD,
    MINOR_SEVENTH,
    MINOR_SIXTH,
    MINOR_THIRD,
    Interval,
)
from music_tools.scale import (
    ConcreteScale,
    interval_sequence,
    name_to_scale,
    scale_from_intervals,
    scale_with_root,
)


def test_next_mode() -> None:
    major = name_to_scale["Major"]
    maybe_dorian = next_mode(major)
    dorian_intervals = interval_sequence([2, 1, 2, 2, 2, 1, 2])
    assert maybe_dorian == scale_from_intervals(dorian_intervals)


def test_diminished_modes() -> None:
    """Symmetric diminished scale only had 2 modes"""
    dim = name_to_scale["Whole-Half Diminished"]
    modes = list(scale_modes(dim))
    assert modes == [
        dim,
        scale_from_intervals(interval_sequence([1, 2, 1, 2, 1, 2, 1, 2])),
    ]


def test_whole_tone_modes() -> None:
    """Symmetric whole tone scale only had 1 modes"""
    whole = name_to_scale["Whole-Tone"]
    modes = list(scale_modes(whole))
    assert modes == [whole]


def test_major_modes() -> None:
    """Each mode with a major scale root should all be equivalent to C major"""
    concrete_modes = starmap(
        scale_with_root,
        zip(
            map(n, ("C", "D", "E", "F", "G", "A", "B")),
            major_scale_modes_by_name.values(),
        ),
    )

    def sort_mode(mode: ConcreteScale) -> ConcreteScale:
        return ConcreteScale(tuple(sorted(mode)))

    sorted_modes = list(map(sort_mode, concrete_modes))

    assert all((sorted_mode == sorted_modes[0] for sorted_mode in sorted_modes))


def test_major_modes_repr() -> None:
    """Each mode with a major scale root should all be equivalent to C major"""
    assert list(map(str, major_scale_modes_by_name.values())) == [
        "(1 2 3 4 5 6 7)",
        "(1 2 ♭3 4 5 6 ♭7)",
        "(1 ♭2 ♭3 4 5 ♭6 ♭7)",
        "(1 2 3 ♯4 5 6 7)",
        "(1 2 3 4 5 6 ♭7)",
        "(1 2 ♭3 4 5 ♭6 ♭7)",
        "(1 ♭2 ♭3 4 ♭5 ♭6 ♭7)",
    ]


class TestEditsRepr:
    def test_no_edits(self) -> None:
        edits: Edits[Interval] = Edits(tuple(), 0)
        assert _edits_repr(edits) == ""

    def test_replace_one_flat(self) -> None:
        edits: Edits[Interval] = Edits(
            (EditOp(MAJOR_THIRD, MINOR_THIRD, 2),),
            0,
        )
        assert _edits_repr(edits) == "♭3"

    def test_replace_one_natural(self) -> None:
        edits: Edits[Interval] = Edits(
            (EditOp(MINOR_THIRD, MAJOR_THIRD, 2),),
            0,
        )
        assert _edits_repr(edits) == "♮3"

    def test_replace_one_sharp(self) -> None:
        edits: Edits[Interval] = Edits(
            (EditOp(MAJOR_SECOND, MINOR_THIRD, 1),),
            0,
        )
        assert _edits_repr(edits) == "♯2"

    def test_replace_three(self) -> None:
        edits: Edits[Interval] = Edits(
            (
                EditOp(MAJOR_THIRD, MINOR_THIRD, 2),
                EditOp(MAJOR_SIXTH, MINOR_SIXTH, 5),
                EditOp(MAJOR_SEVENTH, MINOR_SEVENTH, 6),
            ),
            0,
        )
        assert _edits_repr(edits) == "♭3 ♭6 ♭7"

    def test_insert_remove(self) -> None:
        edits: Edits[Interval] = Edits(
            (
                EditOp(None, MAJOR_THIRD, 2),
                EditOp(MAJOR_SIXTH, None, 5),
            ),
            0,
        )
        assert _edits_repr(edits) == "+♮3 -♮6"
