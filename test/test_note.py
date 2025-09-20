from music_tools.pitch import Octave
import pytest

from music_tools.note import (
    Accidental,
    MusicalPitch,
    Note,
    note_name_parser,
    NoteName,
    accidental_parser,
    note_parser,
    musical_pitch_parser,
)
from parsy import ParseError  # type: ignore


def test_note_name_parser():
    assert note_name_parser.parse("A") == NoteName.A
    assert note_name_parser.parse("B") == NoteName.B
    assert note_name_parser.parse("C") == NoteName.C
    assert note_name_parser.parse("D") == NoteName.D
    assert note_name_parser.parse("E") == NoteName.E
    assert note_name_parser.parse("F") == NoteName.F
    assert note_name_parser.parse("G") == NoteName.G

    with pytest.raises(ParseError):
        note_name_parser.parse("X")


def test_accidental_parser():
    assert accidental_parser.parse("bb") == Accidental.DoubleFlat
    assert accidental_parser.parse("b") == Accidental.Flat
    assert accidental_parser.parse("") == Accidental.Natural
    assert accidental_parser.parse("#") == Accidental.Sharp
    assert accidental_parser.parse("##") == Accidental.DoubleSharp

    with pytest.raises(ParseError):
        accidental_parser.parse("bbb")

    with pytest.raises(ParseError):
        accidental_parser.parse("###")

    with pytest.raises(ParseError):
        accidental_parser.parse("#b#")


def test_note_parser():
    assert note_parser.parse("A#") == Note(NoteName.A, Accidental.Sharp)


def test_musical_pitch_parser():
    assert musical_pitch_parser.parse("Bb4") == MusicalPitch(
        Note(NoteName.B, Accidental.Flat), Octave(4)
    )


# def test_parser():
#     result = note_name_parser.parse("E")
#     assert result == NoteName.E
