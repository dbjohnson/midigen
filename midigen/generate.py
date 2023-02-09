import argparse
from midigen.notes import Note
from midigen.keys import Key, Mode
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k',
        '--key',
        default='C'
    )

    parser.add_argument(
        '-c',
        '--chord',
        required=True,
        help='Chords to generate (Cmaj7, Dm7, etc. or ii, V7, Imaj7, etc.)',
        nargs='+'
    )

    parser.add_argument(
        '-l',
        '--loop',
        required=False,
        type=int,
        default=0,
        help='Number of times to loop the chord progression',
    )

    parser.add_argument(
        '-o',
        default='output.mid',
        help='output file'
    )

    args = parser.parse_args()

    chords = [Key.parse_chord(args.key + chord) for chord in args.chord]
