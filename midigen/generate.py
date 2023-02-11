import argparse
import time

import mido

from midigen.keys import Key
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track, Song
from midigen import rhythm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k',
        '--key',
        default='C'
    )

    parser.add_argument(
        '-c',
        '--chords',
        required=True,
        help='Chords to generate (Cmaj7, Dm7, etc. or ii, V7, Imaj7, etc.)',
        nargs='+'
    )

    parser.add_argument(
        '-r',
        '--rhythm',
        type=str,
        help='Canned rhythm to use',
    )

    parser.add_argument(
        '-t',
        '--tempo',
        required=False,
        type=int,
        default=90,
        help='tempo in BPM',
    )

    parser.add_argument(
        '-o',
        '--output',
        default='output.mid',
        help='output file'
    )

    parser.add_argument(
        '-l',
        '--loop',
        type=int,
        default=1,
        help='loop n times'
    )

    parser.add_argument(
        '-p',
        '--play',
        default=False,
        action='store_true',
        help='play the chord progression'
    )

    args = parser.parse_args()

    chords = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                Key.parse_chord(args.key + chord)
            ] * 4,
            time_signature=TimeSignature(4, 4),
            tempo=args.tempo,
            velocity=90
        )
        for chord in args.chords
    ],
        channel=1,
        name='chords',
    )

    beat = Track.from_measures([
        pattern(
            tempo=args.tempo,
            velocity=127,
        )
        for pattern in (
            rhythm.four_on_the_floor,
            rhythm.son_clave,
            rhythm.straight_16th
        )
    ],
        stack=True
    ).loop(len(args.chords))

    song = Song([beat, chords])

    if args.play:
        port = mido.open_output('midigen', virtual=True)
        time.sleep(2)
        song.loop(port, args.loop)

    song.to_midi(args.output)


if __name__ == '__main__':
    main()
