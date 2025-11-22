from math import sqrt
from music_tools.algorithms import (
    EditOp,
    LevenshteinEditMatrix,
    SubsequenceSearcher,
    EditSequence,
)
from music_tools.pitch import (
    MAJOR_SEVENTH,
    MAJOR_SIXTH,
    MAJOR_THIRD,
    MINOR_SEVENTH,
    MINOR_SIXTH,
    MINOR_THIRD,
    Interval,
)
from music_tools.scale import (
    _interval_cost,
    name_to_scale,
)


def test_minor_pentatonic_in_major() -> None:
    # major scale
    seq = (2, 2, 1, 2, 2, 2, 1)

    # minor pentatonic
    subseq = (3, 2, 2, 3, 2)

    searcher = SubsequenceSearcher(seq)

    indices = list(searcher.find_subsequence_indices(subseq))
    # dorian, phrygian, aeolian - the minor modes
    assert indices == [1, 2, 5]


def test_levenshtein_strings() -> None:
    left = "hello"
    right = "yellow"

    def cost(edit: EditOp[str]) -> float:
        return 1 if edit.left_value != edit.right_value else 0

    matrix = LevenshteinEditMatrix[str](left, right, cost)
    assert matrix.at(0, 0) == EditSequence((EditOp("h", "y", 0),), 1)
    assert matrix.at(4, 5) == EditSequence(
        (EditOp("h", "y", 0), EditOp(None, "w", 5)), 2
    )
    assert matrix.at(4, 5) == matrix.best_edit_sequence()

    matrix = LevenshteinEditMatrix[str](right, left, cost)
    assert matrix.at(0, 0) == EditSequence((EditOp("y", "h", 0),), 1)
    assert matrix.at(5, 4) == EditSequence(
        (EditOp("y", "h", 0), EditOp("w", None, 5)), 2
    )
    assert matrix.at(5, 4) == matrix.best_edit_sequence()


def test_levenshtein_major_to_minor() -> None:
    major = name_to_scale["Major"]
    minor = name_to_scale["Minor"]

    matrix = LevenshteinEditMatrix[Interval](major, minor, _interval_cost)
    assert matrix.best_edit_sequence() == EditSequence(
        (
            EditOp(MAJOR_THIRD, MINOR_THIRD, 2),
            EditOp(MAJOR_SIXTH, MINOR_SIXTH, 5),
            EditOp(MAJOR_SEVENTH, MINOR_SEVENTH, 6),
        ),
        3,
    )


def test_levenshtein_minor_to_harmonic() -> None:
    minor = name_to_scale["Minor"]
    harmonic = name_to_scale["Harmonic Minor"]

    matrix = LevenshteinEditMatrix[Interval](minor, harmonic, _interval_cost)
    assert matrix.best_edit_sequence() == EditSequence(
        (EditOp(MINOR_SEVENTH, MAJOR_SEVENTH, 6),),
        1,
    )
