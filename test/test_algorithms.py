from music_tools.algorithms import SubsequenceSearcher


def test_minor_pentatonic_in_major():
    # major scale
    seq = (2, 2, 1, 2, 2, 2, 1)

    # minor pentatonic
    subseq = (3, 2, 2, 3, 2)

    searcher = SubsequenceSearcher(seq)

    indices = list(searcher.find_subsequence_indices(subseq))
    # dorian, phrygian, aeolian - the minor modes
    assert indices == [1, 2, 5]
