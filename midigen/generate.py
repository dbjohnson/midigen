import os
import argparse
import time

import mido

from midigen.keys import Key
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Track, Song
from midigen.humanize import randomize_time, randomize_velocity, swing, pulse, dropout
from midigen.instruments import INSTRUMENTS
from midigen.markov import Graph
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

    parser.add_argument(
        '-a',
        '--ableton',
        default=False,
        action='store_true',
        help='open ableton for playback (macOS only)',
    )

    args = parser.parse_args()

    keys = [Key.parse(args.key + chord) for chord in args.chords]

    def humanize(measure):
        for mutator, amount in (
            (pulse, 0.1),
            (randomize_time, args.randomize),
            (randomize_velocity, args.randomize),
            (swing, args.swing),
            (dropout, 0.1)
        ):
            measure = mutator(measure, amount)
        return measure

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
            pattern=Graph(
                key,
                octave_min=0,
                octave_max=2
            ).strengthen_connections(
                # strong attractor back to root / fifth
                [
                    (key.note(degree), key.note(target))
                    for degree in range(2, 8)
                    for target in (1, 5)
                ],
                5
            ).generate_sequence(4),
            time_signature=TimeSignature(4, 4),
            velocity=120,
            duration=0.7
        ).mutate(humanize)
        for _ in range(args.loop)
        for key, extensions in keys
    ],
        channel=0,
        program=INSTRUMENTS['Acoustic Bass'],
        name='bass',
    )

    chords = Track.from_measures([
        Measure.from_pattern(
            pattern=[
                # keep chords close to the key's root triad
                key.chord(match_voicing=key.triad())[1:]  # drop root
            ] * 4,
            time_signature=TimeSignature(4, 4),
            velocity=60,
            duration=0.7
        ).mutate(humanize)
        for _ in range(args.loop)
        for key, extensions in keys
    ],
        channel=1,
        name='chords',
    )

    melody = Track.from_measures([
        Measure.from_pattern(
            pattern=Graph(
                key=key,
                octave_min=3,
                octave_max=4,
            ).generate_sequence(8),
            time_signature=TimeSignature(4, 4),
            velocity=90,
            duration=0.7
        ).mutate(humanize).mutate(dropout).mutate(dropout)
        for _ in range(args.loop)
        for key, extensions in keys
    ],
        channel=2,
        program=INSTRUMENTS['Vibraphone'],
        name='melody',
    )

    song = Song([
        beat, bass, chords, melody
    ])

    if args.output:
        song.to_midi(args.output, tempo=args.tempo)

    if args.play:
        if args.ableton:
            os.system(f'open "{os.path.join(os.path.dirname(__file__), "midigen.als")}"')
        port = mido.open_output(args.name, virtual=True)
        time.sleep(2)
        port.panic()  # clear anything that was previous playing
        song.play(port, args.tempo)


if __name__ == '__main__':
    main()
