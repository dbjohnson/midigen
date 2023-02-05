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
        self.notes = [
            list(Note)[(key.value + mode.value + interval) % len(Note)].value
            for interval in [0, 2, 4, 5, 7, 9, 11, 12]
        ]

    def play(self, port, duration=1.0, tempo=80):
        Sequencer().play(port, [
            Message(
                'note_on',
                note=note,
                velocity=127,
                time=tempo / 60 * duration
            )
            for note in self.notes
        ], tempo)


class Chord:
    def __init__(
        self,
        key: Note,
        degree: int,
        form: ChordForm = ChordForm.Triad
    ):
        self.scale = Scale(key, list(Mode)[degree])
        self.notes = [
            self.scale.notes[i] for i in form.value
        ]

    def play(self, port, duration=1.0, velocity=80):
        for note in self.notes:
            port.send(Message('note_on', note=note, velocity=velocity))