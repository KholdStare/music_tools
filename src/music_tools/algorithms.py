from typing import Generic, Iterable, Protocol, TypeVar
from typing_extensions import Self

T = TypeVar("T")


class SequenceElement(Protocol):
    def __add__(self, x: Self, /) -> Self: ...
    def __gt__(self, x: Self, /) -> Self: ...


S = TypeVar("S", bound=SequenceElement)


def _transpose(matrix: Iterable[list[T]]) -> list[list[T]]:
    return list(map(list, zip(*matrix, strict=True)))


class SubsequenceSearcher(Generic[S]):
    """Searches for subsequences in a circular sequence."""

    def __init__(self, parent_sequence: Iterable[S]):
        sequence_list = list(parent_sequence)
        sequence_length = len(sequence_list)
        sequence_sum = sum(sequence_list)

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

    def find_subsequence_indices(self, subsequence: Iterable[S]) -> Iterable[int]:
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
