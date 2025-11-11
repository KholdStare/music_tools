from music_tools.pitch import (
    DIMINISHED_FIFTH,
    DIMINISHED_SEVENTH,
    FIFTH,
    FOURTH,
    MAJOR_SECOND,
    MAJOR_SEVENTH,
    MAJOR_SIXTH,
    MAJOR_THIRD,
    MINOR_THIRD,
    UNISON,
)
from music_tools.scale import (
    Scale,
    gen_conventional_scales,
    interval_sequence,
    intervals_from_scale,
    scale_from_intervals,
)


def test_number_of_modes() -> None:
    scales = list(gen_conventional_scales())
    assert len(scales) == 33


_major_scale = Scale(
    (
        UNISON,
        MAJOR_SECOND,
        MAJOR_THIRD,
        FOURTH,
        FIFTH,
        MAJOR_SIXTH,
        MAJOR_SEVENTH,
    )
)


def test_scale_repr() -> None:
    assert str(_major_scale) == "(1 2 3 4 5 6 7)"


class TestScaleFromIntervals:
    def test_major(self) -> None:
        major_intervals = interval_sequence([2, 2, 1, 2, 2, 2, 1])
        assert scale_from_intervals(major_intervals) == _major_scale

    def test_less_than_octave(self) -> None:
        major_intervals = interval_sequence([2, 2, 1, 2, 2, 2])
        assert scale_from_intervals(major_intervals) == _major_scale

    def test_more_than_octave(self) -> None:
        major_intervals_in_large_jumps = interval_sequence([2, 14, 1, 14, 2, 14])
        assert scale_from_intervals(major_intervals_in_large_jumps) == _major_scale

    def test_overlapping(self) -> None:
        diminished_intervals = interval_sequence([3, 3, 3, 3, 3, 3, 3])
        diminished_chord = Scale(
            (
                UNISON,
                MINOR_THIRD,
                DIMINISHED_FIFTH,
                DIMINISHED_SEVENTH,
            )
        )
        assert scale_from_intervals(diminished_intervals) == diminished_chord

    def test_round_trip(self) -> None:
        major_intervals = interval_sequence([2, 2, 1, 2, 2, 2])
        intervals = intervals_from_scale(scale_from_intervals(major_intervals))

        assert intervals == major_intervals
