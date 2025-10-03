from music_tools.guitar import (
    EADGBE,
    MEGA_FRETBOARD,
    FretboardAnnotation,
    FretboardLocation,
    render_fretboard_ascii,
)
from music_tools.pitch import (
    FIFTH,
    MAJOR_SEVENTH,
    MAJOR_THIRD,
    OctavePitch,
)
from music_tools.note import (
    Note,
    note_parser,
)

# TODO: categorize each generated scale as mode of some parent scale


class TermColor:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def major_7_annotation(root_note: Note) -> FretboardAnnotation[str]:
    root: OctavePitch = root_note.to_octave_pitch()
    pitches: dict[OctavePitch, str] = {
        root: f"{TermColor.GREEN}1{TermColor.ENDC}",
        root + MAJOR_THIRD: f"{TermColor.BLUE}3{TermColor.ENDC}",
        root + FIFTH: f"{TermColor.CYAN}5{TermColor.ENDC}",
        root + MAJOR_SEVENTH: f"{TermColor.YELLOW}7{TermColor.ENDC}",
    }

    def annotation(loc: FretboardLocation) -> str | None:
        string, fret, pitch = loc
        return pitches.get(pitch.to_octave()[1])

    return annotation


def main():
    c_maj_7 = major_7_annotation(note_parser.parse("C"))

    print(render_fretboard_ascii(EADGBE, 24, c_maj_7))

    print()

    print(render_fretboard_ascii(MEGA_FRETBOARD, 24, c_maj_7))


if __name__ == "__main__":
    main()
