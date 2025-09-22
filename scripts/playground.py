from music_tools.guitar import EADGBE, render_fretboard_ascii
from music_tools.pitch import Octave
from music_tools.note import (
    Note,
    NoteName,
    Accidental,
    MusicalPitch,
    sharp_notes,
    flat_notes,
)
from music_tools.scale import gen_conventional_scales, scale_with_root, name_to_scale

# TODO: categorize each generated scale as mode of some parent scale


def main():
    a4 = MusicalPitch(Note(NoteName.A, Accidental.Natural), Octave(4))
    print(a4)
    print(sharp_notes)
    print(flat_notes)
    print(name_to_scale["Major"])
    for note in sharp_notes:
        print(f"{note} major", scale_with_root(note, name_to_scale["Major"]))

    all_scales = list(gen_conventional_scales())
    print(len(all_scales))
    for scale in all_scales:
        print(scale_with_root(Note(NoteName.C), scale))

    print(render_fretboard_ascii(EADGBE, 12))


if __name__ == "__main__":
    main()
