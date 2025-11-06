from music_tools.mode import next_mode, scale_modes
from music_tools.scale import interval_sequence, name_to_scale, scale_from_intervals


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
