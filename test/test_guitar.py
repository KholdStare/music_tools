from music_tools.guitar import EADGBE, FretIndex, StringIndex, render_fretboard_ascii


def test_ascii_example1():
    def annot(loc: tuple[StringIndex, FretIndex]) -> str | None:
        return "O" if loc == (StringIndex(2), FretIndex(3)) else None

    result = render_fretboard_ascii(EADGBE, 4, annot)

    expected = """
E  |---|---|---|---|
B  |---|---|--O|---|
G  |---|---|---|---|
D  |---|---|---|---|
A  |---|---|---|---|
E  |---|---|---|---|
     1       3     
""".strip("\n")

    assert result == expected
