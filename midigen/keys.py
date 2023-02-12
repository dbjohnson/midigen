import re
from typing import List
from enum import Enum
from itertools import product

from midigen.sequencer import Track
from midigen.notes import Note
from midigen.time import Measure, TimeSignature


class Mode(Enum):
    Ionian = 1
    Dorian = 2
    Phrygian = 3
    Lydian = 4
    Mixolydian = 5
    Aeolian = 6
    Locrian = 7
    I = 1  # noqa
    ii = 2
    iii = 3
    IV = 4
    V = 5
    vi = 6
    vii = 7
    Major = 1
    Minor = 6
    Diminished = 7

    def __add__(self, offset: int):
        for mode in Mode:
            if (mode.value) % 8 == (self.value + offset) % 8:
                return mode

    def __sub__(self, offset: int):
        return self + (-offset)


class Key:
    def __init__(self, key: Note, mode: Mode = Mode.Major):
        self.key = key
        self.mode = mode

        # find the intervals by rotating the ionian mode
        # intervals by the mode value
        self.intervals = _rotate(
            [2, 2, 1, 2, 2, 2, 1],
            mode.value - 1
        )

        self.notes = [
            key + sum(self.intervals[:i])
            for i in range(len(self.intervals))
        ]

        self.note_values = [
            note.value + (12 if note.value < self.key.value else 0)
            for note in self.notes
        ]

    def relative_key(self, degree):
        return Key(
            self.note(degree),
            self.mode + (degree - 1)
        )

    def note(self, degree: int):
        return self.notes[(degree - 1) % len(self.notes)]

    def to_track(
        self,
        velocity: int = 127,
        duration: float = 1.0,
        tempo: float = 180
    ):
        """
        Generate an ascending scale track
        """
        return Track.from_measures([
            Measure.from_pattern(
                pattern=[
                    [note]
                    for note in _rectify(
                        self.note_values + [self.note_values[0]]
                    )
                ],
                time_signature=TimeSignature(8, 4),
                tempo=tempo,
                velocity=velocity,
                duration=duration
            )
        ])

    def triad(self, inversion: int = 0):
        return self.__chord([1, 3, 5], inversion)

    def shell(self):
        return self.__chord([3, 7])

    @staticmethod
    def parse(key: str):
        match = re.match(
            (
                r'(?P<note>([A-Ga-g][b|#]?)?)'
                r'(?P<degree>[iIV]*)'
                r'(?P<mode>(maj|min|m|M)?)'
                r'(?P<sus>(sus)?)'
                r'(?P<ext>(ext)?[0-9]*)'
            ),
            key,
            re.IGNORECASE
        ).groupdict()

        return Key(
            Note[match['note'].replace('#', '_SHARP') or 'C'],
            Mode[{
                'm': 'Minor',
                'min': 'Minor',
                'maj': 'Major',
                'Maj': 'Major',
                'M': 'Major',
            }[(match['mode'] or 'M').title()]],
        ).relative_key(
            Mode[match['degree'] or 'I'].value
        ), match['ext']

    @staticmethod
    def parse_chord(chord: str):
        key, ext = Key.parse(chord)
        return key.chord(
            list(range(7, int(ext or '5') + 1, 2))
        )

    def chord(
        self,
        extensions=[],
        inversion: int = 0,
        match_voicing: List[int] = None
    ):
        notes = self.__chord(
            [1, 3, 5] + extensions,
            inversion
        )

        if match_voicing:
            # find a voicing that best matches the indicated tones
            return min([
                [
                    n + o for n, o in zip(notes, offsets)
                ]
                for offsets in product(
                    [-12, 0, 12],
                    repeat=len(notes)
                )
            ],
                key=lambda voicing: sum([
                    abs(n - m)
                    for n, m in product(voicing, match_voicing)
                ])
            )
        else:
            return notes

    def __chord(self, notes, inversion: int = 0):
        assert 0 <= inversion < len(notes)
        return _rectify(
            _rotate(
                [
                    # every other note up to the 13th degree
                    self.note(i).value - (12 if inversion > 0 else 0)
                    for i in notes
                ],
                inversion
            )
        )

    def __eq__(self, other: 'Key'):
        return set(self.notes) == set(other.notes)

    def __repr__(self):
        return f'{self.key.name} {self.mode.name}'


def _rotate(seq, n):
    return seq[n:] + seq[:n]


def _rectify(sequence: List[int]):
    """
    ensure note value sequence is monotonically increasing;
    add octaves as necessary
    """
    if sequence != sorted(sequence):
        return _rectify([sequence[0]] + [
            v + (12 if v < prior else 0)
            for v, prior in zip(sequence[1:], sequence)
        ])
    else:
        return sequence
