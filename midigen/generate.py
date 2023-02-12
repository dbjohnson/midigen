import argparse
import time

import mido

from midigen.keys import Key
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track, Song
from midigen.humanize import randomize, add_swing
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
        required=False,
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

    parser.add_argument(
        '-s',
        '--swing',
        default=0.1,
        type=float,
        help='swing amount (0-1)'
    )

    parser.add_argument(
        '-r',
        '--randomize',
        default=0.01,
        type=float,
        help='randomize amount (0-1)'
    )

    args = parser.parse_args()

    def humanize(measure):
        return randomize(
            add_swing(
                measure,
                args.swing
            ),
            args.randomize
        )

    chords = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                Key.parse_chord(args.key + chord)
            ] * 4,
            time_signature=TimeSignature(4, 4),
            tempo=args.tempo,
            velocity=90
        ).mutate(humanize)
        for chord in args.chords
    ],
        channel=1,
        name='chords',
    )

    beat = Track.string_tracks([
        Track.from_measures([
            pattern(
                tempo=args.tempo,
                velocity=127,
            ).mutate(humanize)
            for pattern in (
                rhythm.four_on_the_floor,
                rhythm.son_clave,
                rhythm.straight_16ths
            )
        ],
            stack=True
        )
        for _ in range(len(args.chords))
    ])

    bass = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                [n.value - 24 if n.value >= 24 else n.value]
                for k in [Key.parse(args.key + chord)[0]]
                for n in [k.note(degree) for degree in (1, 3, 5, 1)]
            ],
            time_signature=TimeSignature(4, 4),
            tempo=args.tempo,
            velocity=90
        ).mutate(humanize)
        for chord in args.chords
    ],
        channel=1,
        name='bass',
    )

    song = Song([beat, chords, bass])

    if args.play:
        port = mido.open_output('midigen', virtual=True)
        time.sleep(2)
        song.loop(port, args.loop)

    if args.output:
        song.to_midi(args.output)


if __name__ == '__main__':
    main()
