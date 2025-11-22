from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable, Generic, Iterable, Protocol, TypeVar, Sequence
from typing_extensions import Self

T = TypeVar("T")


class AddableComparable(Protocol):
    def __add__(self, x: Self, /) -> Self: ...
    def __gt__(self, x: Self, /) -> Self: ...


A = TypeVar("A", bound=AddableComparable)


def _transpose(matrix: Iterable[list[T]]) -> list[list[T]]:
    """Transpose a matrix-like list of lists"""
    return list(map(list, zip(*matrix, strict=True)))


class SubsequenceSearcher(Generic[A]):
    """Searches for subsequences in a circular sequence."""

    def __init__(self, parent_sequence: Iterable[A]):
        sequence_list = list(parent_sequence)
        sequence_length = len(sequence_list)
        sequence_sum = sum(sequence_list)  # type: ignore

        # The parent sequence is circular, and the sequence is made of distances
        # to the next element
        # each row in the search matrix is another sequence based on the
        # previous row, where one more element is skipped.
        # transposed_search_matrix[j][i] is distance of the jump from the ith
        # element, j+1 steps
        transposed_search_matrix = [sequence_list]
        for i in range(0, sequence_length - 1):
            transposed_search_matrix.append(
                [
                    x + sequence_list[(i + j + 1) % sequence_length]
                    for (j, x) in enumerate(transposed_search_matrix[i])
                ]
            )

        assert all((x == sequence_sum for x in transposed_search_matrix[-1])), (
            "The final row of transition distances should just loop around the entire sequence"
        )
        transposed_search_matrix.pop()  # we don't need it

        # each row in search_matrix is distances to successive elements
        # search_matrix[i][j] is distance of the jump from the ith
        # element, j+1 steps
        search_matrix = _transpose(transposed_search_matrix)

        # each successive jump in each row is bigger than previous
        # i.e. each row is sorted
        for row in search_matrix:
            for i in range(1, len(row)):
                assert row[i] > row[i - 1]

        self.search_matrix = search_matrix

    def find_subsequence_indices(self, subsequence: Iterable[A]) -> Iterable[int]:
        subseq_list = tuple(subsequence)
        for starting_index, row in enumerate(self.search_matrix):
            current_index = starting_index
            try:
                for subseq_elem in subseq_list:
                    jump_index = row.index(subseq_elem)
                    # get the next row corresponding to next element
                    current_index = (current_index + jump_index + 1) % len(
                        self.search_matrix
                    )
                    row = self.search_matrix[current_index]

                # if we made it through the whole subsequence without getting a
                # ValueError, then subsequence exists at that starting_index
                yield starting_index
            except ValueError:
                continue


class EditOpEnum(IntEnum):
    Insert = 0
    Delete = 1
    Replace = 2


@dataclass(frozen=True)
class EditOp(Generic[T]):
    left_value: T | None
    """Left value being replaced/deleted"""
    right_value: T | None
    """Right value being inserted/replaced with"""
    left_position: int
    """position in left sequence where edit occurs"""


EditCostFunction = Callable[[EditOp[T]], float]
"""Cost function for an edit operation, used to rank edit paths. A cost of zero signifies no edit necessary"""


@dataclass(frozen=True)
class Edits(Generic[T]):
    edits: tuple[EditOp[T], ...]
    cost: float

    @staticmethod
    def make(edits: Iterable[EditOp[T]], cost_func: EditCostFunction[T]) -> Edits[T]:
        edits_tuple = tuple(edits)
        return Edits(edits_tuple, sum(map(cost_func, edits_tuple)))

    def append(self, edit: EditOp[T], cost_func: EditCostFunction[T]) -> Edits[T]:
        new_cost = cost_func(edit)
        # if new edit doesn't cost anything, it's not an edit
        if new_cost == 0.0:
            return self
        return Edits(self.edits + (edit,), self.cost + new_cost)


@dataclass
class LevenshteinEditMatrix(Generic[T]):
    left: Sequence[T]
    right: Sequence[T]
    cost_func: EditCostFunction[T]
    matrix: list[list[Edits[T]]] = field(init=False)

    def __post_init__(self) -> None:
        self.matrix = [[] for _l in self.left]

        # precompute the matrix row by row
        for left_pos in range(0, len(self.left)):
            for right_pos in range(0, len(self.right)):
                self.matrix[left_pos].append(self._calc_sequence(left_pos, right_pos))

    def _calc_sequence(self, left_pos: int, right_pos: int) -> Edits[T]:
        replace_seq = self.at(left_pos - 1, right_pos - 1)
        replace_edit = EditOp(self.left[left_pos], self.right[right_pos], left_pos)
        replace_seq = replace_seq.append(replace_edit, self.cost_func)

        insert_seq = self.at(left_pos, right_pos - 1)
        # TODO: the edit position here is questionable?
        insert_edit = EditOp(None, self.right[right_pos], left_pos + 1)
        insert_seq = insert_seq.append(insert_edit, self.cost_func)

        delete_seq = self.at(left_pos - 1, right_pos)
        delete_edit = EditOp(self.left[left_pos], None, left_pos)
        delete_seq = delete_seq.append(delete_edit, self.cost_func)

        return sorted((replace_seq, insert_seq, delete_seq), key=lambda seq: seq.cost)[
            0
        ]

    def at(self, left_pos: int, right_pos: int) -> Edits[T]:
        if left_pos < 0 or right_pos < 0:
            return Edits(tuple(), 0)

        return self.matrix[left_pos][right_pos]

    def best_edit_sequence(self) -> Edits[T]:
        return self.at(len(self.left) - 1, len(self.right) - 1)


def rank_sequences_by_closeness[T](
    needle: Sequence[T],
    candidates: Iterable[Sequence[T]],
    cost_func: EditCostFunction[T],
) -> list[tuple[Sequence[T], Edits[T]]]:
    with_edit_sequences = [
        (
            candidate,
            LevenshteinEditMatrix(needle, candidate, cost_func).best_edit_sequence(),
        )
        for candidate in candidates
    ]

    return sorted(with_edit_sequences, key=lambda t: t[1].cost)


def without_edits(ranked: list[tuple[Sequence[T], Edits[T]]]) -> list[Sequence[T]]:
    return [t[0] for t in ranked]
