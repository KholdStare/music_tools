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
    Interval,
)
from music_tools.scale import (
    Scale,
    _estimate_scale_degree,
    gen_conventional_scales,
    interval_sequence,
    intervals_from_scale,
    scale_from_intervals,
    name_to_scale,
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


def test_estimate_scale_degree() -> None:
    estimates = [_estimate_scale_degree(Interval(i)) for i in range(24)]
    expected = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6]
    assert estimates == (expected + expected)


class TestScaleRepr:
    def test_major(self) -> None:
        assert str(_major_scale) == "(1 2 3 4 5 6 7)"

    def test_diminished(self) -> None:
        assert str(name_to_scale["Whole-Half Diminished"]) == "(1 2 ♭3 4 ♭5 ♭6 6 7)"

    def test_whole_tone(self) -> None:
        assert str(name_to_scale["Whole-Tone"]) == "(1 2 3 ♭5 ♭6 ♭7)"

    def test_augmented(self) -> None:
        assert str(name_to_scale["Augmented"]) == "(1 ♭3 3 5 ♭6 7)"


# TODO: test other scale reprs, especially when less/more than 7 degrees


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
