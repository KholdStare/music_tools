from music_tools.scale import gen_conventional_scales

def test_number_of_modes():
    scales = list(gen_conventional_scales())
    assert len(scales) == 33