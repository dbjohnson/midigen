import argparse

import mido

from midigen.keys import Key
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track, Song


if __name__ == '__main__':
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
        '-p',
        '--play',
        default=False,
        action='store_true',
        help='play the chord progression'
    )

    args = parser.parse_args()

    track = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                Key.parse_chord(args.key + chord)
            ] * 4,
            time_signature=TimeSignature(4, 4),
            tempo=args.tempo,
            velocity=90
        )
        for chord in args.chords
    ], name='chords')

    if args.play:
        port = mido.open_output('midigen', virtual=True)
        track.play(port, block=True)

    Song([track]).to_midi(args.output)
