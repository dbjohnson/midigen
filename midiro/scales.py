from enum import Enum
from mido import Message
from midiro.sequencer import Sequencer
from midiro.note import Note


class Mode(Enum):
    Ionian = 1
    Dorian = 2
    Phrygian = 3
    Lydian = 4
    Mixolydian = 5
    Aeolian = 6
    Locrian = 7
    Major = 1
    Minor = 6


class ChordForm(Enum):
    Triad = [0, 2, 4]
    Seventh = [0, 2, 4, 6]
    Ninth = [0, 2, 4, 6, 8]
    Eleventh = [0, 2, 4, 6, 8, 10]
    Thirteenth = [0, 2, 4, 6, 8, 10, 12]


class Scale:
    def __init__(self, key: Note, mode: Mode):
        self.key = key
        self.mode = mode

        self.intervals = [
            [2, 2, 1, 2, 2, 2, 1][
                (degree + mode.value - 1) % 7
            ]
            for degree in range(7)
        ]

        self.notes = [
            list(Note)[(
                key.value + sum(self.intervals[:i])
            ) % len(Note)]
            for i in range(len(self.intervals))
        ]

    def play(self, port, velocity=127, duration=1.0, tempo=180):
        Sequencer().play(port, [
            Message(
                'note_on',
                note=note + (12 if note < self.key.value else 0),
                velocity=velocity,
                time=duration
            )
            for note in [n.value for n in self.notes] + [self.key.value + 12]
        ], tempo)


class Chord:
    def __init__(
        self,
        key: Note,
        degree: int,
        form: ChordForm = ChordForm.Triad
    ):
        self.scale = Scale(key, Mode.Ionian)
        self.notes = [
            self.scale.notes[(i + degree - 1) % len(self.scale.notes)]
            for i in form.value
        ]

    def play(self, port, duration=1.0, velocity=80):
        for note in self.notes:
            port.send(Message(
                'note_on',
                note=note.value,
                velocity=velocity
            ))