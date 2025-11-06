from music_tools.guitar import (
    EADGBE,
    MEGA_FRETBOARD,
    T,
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
    n,
    note_parser,
)
from music_tools.scale import ConcreteScale, name_to_scale, scale_with_root
from music_tools.mode import major_scale_modes_by_name

# TODO: categorize each generated scale as mode of some parent scale


class TermColor:
    HEADER = "\033[95m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38:5:214m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


COLOR_GRADIENT = [
    TermColor.BOLD,
    TermColor.GREEN,
    TermColor.CYAN,
    TermColor.BLUE,
    TermColor.MAGENTA,
    TermColor.RED,
    TermColor.ORANGE,
    TermColor.YELLOW,
]


# TODO: add more options, make them optional
def focus_vertically(
    annotation: FretboardAnnotation[T], *, start_note: Note, max_notes_per_string: int
) -> FretboardAnnotation[T]:
    # TODO:
    # seen_per_string

    def new_annotation(loc: FretboardLocation) -> T | None:
        pass

    return new_annotation


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


# TODO: algorithmically determine "CAGED" shapes


def n_note_per_string(
    n_per_string: int, scale: ConcreteScale
) -> FretboardAnnotation[str]:
    octave_pitches = [n.to_octave_pitch() for n in scale]

    assert n_per_string <= 4, "Not for spider hands"

    def annotation(loc: FretboardLocation) -> str | None:
        string, fret, pitch = loc
        octave, octave_pitch = pitch.to_octave()
        try:
            # index inside the scale
            index = octave_pitches.index(octave_pitch)
            # overall note count across all octaves
            count = octave * 7 + index
            result = f"{COLOR_GRADIENT[count % 3]}{index + 1}{TermColor.ENDC}"
            return result
        except ValueError:
            return None

    return annotation


def main() -> None:
    c_maj_7 = major_7_annotation(note_parser.parse("C"))

    print(render_fretboard_ascii(EADGBE, 24, [c_maj_7]))

    print()

    # print(render_fretboard_ascii(MEGA_FRETBOARD, 24, c_maj_7))

    # c_maj_scale = n_note_per_string(3, scale_with_root(n("C"), name_to_scale["Major"]))

    # print(render_fretboard_ascii(MEGA_FRETBOARD, 24, [c_maj_scale]))

    print(major_scale_modes_by_name)


if __name__ == "__main__":
    main()
