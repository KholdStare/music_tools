from math import sqrt
from music_tools.algorithms import (
    EditOp,
    LevenshteinEditMatrix,
    SubsequenceSearcher,
    Edits,
    rank_sequences_by_closeness,
    without_edits,
    zip_with_next,
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


class TestZipWithNext:
    def test_empty(self) -> None:
        result: list[tuple[int, int]] = list(zip_with_next([]))
        assert result == []

    def test_one(self) -> None:
        result: list[tuple[int, int]] = list(zip_with_next([42]))
        assert result == [(42, 42)]

    def test_many(self) -> None:
        result: list[tuple[int, int]] = list(zip_with_next(range(5)))
        assert result == [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


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
    assert matrix.at(0, 0) == Edits((EditOp("h", "y", 0),), 1)
    assert matrix.at(4, 5) == Edits((EditOp("h", "y", 0), EditOp(None, "w", 5)), 2)
    assert matrix.at(4, 5) == matrix.best_edits()

    matrix = LevenshteinEditMatrix[str](right, left, cost)
    assert matrix.at(0, 0) == Edits((EditOp("y", "h", 0),), 1)
    assert matrix.at(5, 4) == Edits((EditOp("y", "h", 0), EditOp("w", None, 5)), 2)
    assert matrix.at(5, 4) == matrix.best_edits()


def test_levenshtein_major_to_minor() -> None:
    major = name_to_scale["Major"]
    minor = name_to_scale["Minor"]

    matrix = LevenshteinEditMatrix[Interval](major, minor, _interval_cost)
    assert matrix.best_edits() == Edits(
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
    assert matrix.best_edits() == Edits(
        (EditOp(MINOR_SEVENTH, MAJOR_SEVENTH, 6),),
        1,
    )


def _test_cost(op: EditOp[int]) -> float:
    return sqrt(abs((op.left_value or 0) - (op.right_value or 0)))


def test_rank() -> None:
    needle = [1, 4, 6, 8, 10]

    haystack = [
        [1, 4, 7, 8, 10],
        [1, 3, 6, 9, 10],
    ]

    sorted_haystack = without_edits(
        rank_sequences_by_closeness(needle, haystack, _test_cost)
    )
    assert sorted_haystack == haystack


def test_rank_exact_match_and_near_match() -> None:
    needle = [2, 4, 6]

    haystack = [
        [2, 4, 6],  # exact match → should rank first
        [2, 4, 7],
        [1, 4, 6],
    ]

    sorted_haystack = without_edits(
        rank_sequences_by_closeness(needle, haystack, _test_cost)
    )
    assert sorted_haystack == haystack


def test_rank_all_ties() -> None:
    needle = [1, 1, 1]

    haystack = [
        [0, 1, 2],  # distance 1+0+1 = 2
        [2, 1, 0],  # distance 1+0+1 = 2
        [1, 0, 2],  # distance 0+1+1 = 2
    ]

    sorted_haystack = without_edits(
        rank_sequences_by_closeness(needle, haystack, _test_cost)
    )
    assert sorted_haystack == haystack


def test_rank_minor_differences_vs_one_big_one() -> None:
    needle = [1, 1, 1]

    haystack = [
        [2, 2, 1],
        [1, 1, 3],
    ]

    sorted_haystack = without_edits(
        rank_sequences_by_closeness(needle, haystack, _test_cost)
    )
    assert sorted_haystack == list(reversed(haystack))
