import argparse
import random
import time

import mido

from midigen.keys import Key
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track, Song
from midigen.humanize import randomize_time, randomize_velocity, swing, pulse
from midigen.instruments import INSTRUMENTS
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
        default=0.03,
        type=float,
        help='swing amount (0-1)'
    )

    parser.add_argument(
        '-r',
        '--randomize',
        default=0.001,
        type=float,
        help='randomize amount (0-1)'
    )

    parser.add_argument(
        '-n',
        '--name',
        default='midigen',
        help='midi port name'
    )

    args = parser.parse_args()

    def humanize(measure):
        return randomize_velocity(
            randomize_time(
                swing(
                    pulse(measure),
                    args.swing
                ),
                args.randomize
            ),
            args.randomize
        )

    beat = Track.string_tracks([
        Track.from_measures([
            pattern(
                velocity=90,
            ).mutate(humanize)
            for pattern in (
                rhythm.four_on_the_floor,
                rhythm.son_clave,
                rhythm.straight_16ths
            )
        ],
            channel=9,
            stack=True,
            name='beat'
        )
        for _ in range(args.loop)
        for _ in range(len(args.chords))
    ])

    bass = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                [k.note(degree).value - 24]
                for k in [Key.parse(args.key + chord)[0]]
                # always play root downbeat
                for degree in random.choices([1,], k=1) + random.choices(
                    [1, 2, 3, 5, 7],
                    k=3
                )
            ],
            time_signature=TimeSignature(4, 4),
            velocity=120,
            duration=0.7
        ).mutate(humanize)
        for _ in range(args.loop)
        for chord in args.chords
    ],
        channel=0,
        program=INSTRUMENTS['Acoustic Bass'],
        name='bass',
    )

    chords = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                Key.parse_chord(
                    args.key + chord,
                    # keep chords close to the key's root triad
                    match_voicing=Key.parse_chord(args.key)
                )
            ] * 4,
            time_signature=TimeSignature(4, 4),
            velocity=60,
            duration=0.7
        ).mutate(humanize)
        for _ in range(args.loop)
        for chord in args.chords
    ],
        channel=1,
        name='chords',
    )

    melody = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                [k.note(degree).value + 12] if degree else None
                for k in [Key.parse(args.key + chord)[0]]
                for degree in random.choices(
                    [1, 2, 3, 5, 7] + [None] * 2,
                    k=8
                )
            ],
            time_signature=TimeSignature(4, 4),
            velocity=90,
            duration=0.99
        ).mutate(humanize)
        for _ in range(args.loop)
        for chord in args.chords
    ],
        channel=2,
        name='melody',
    )
    song = Song([
        beat, bass, chords, melody
    ])

    if args.output:
        song.to_midi(args.output, tempo=args.tempo)

    if args.play:
        port = mido.open_output(args.name, virtual=True)
        time.sleep(2)
        port.panic()  # clear anything that was previous playing
        song.play(port, args.tempo)


if __name__ == '__main__':
    main()
