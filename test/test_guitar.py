from music_tools.guitar import (
    EADGBE,
    FretIndex,
    FretboardLocation,
    String,
    StringIndex,
    render_fretboard_ascii,
)
from music_tools.note import p


def test_ascii_example1():
    def annot(loc: FretboardLocation) -> str | None:
        return "O" if (loc[0], loc[1]) == (StringIndex(2), FretIndex(3)) else None

    result = render_fretboard_ascii(EADGBE, 4, annot)

    expected = """
E    |---|---|---|---|
B    |---|---|-O-|---|
G    |---|---|---|---|
D    |---|---|---|---|
A    |---|---|---|---|
E    |---|---|---|---|
       1       3     
""".strip("\n")

    assert result == expected


def test_string():
    s = String(p("B2").to_pitch())
    assert s[1] == p("C3").to_pitch()


def test_standard_tuning():
    [high_e, b, g, d, a, low_e] = EADGBE.strings

    assert low_e[5] == a.open_pitch
    assert a[5] == d.open_pitch
    assert d[5] == g.open_pitch
    assert g[4] == b.open_pitch
    assert b[5] == high_e.open_pitch
