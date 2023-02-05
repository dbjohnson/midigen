from enum import Enum
from midiro.sequencer import Track
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
    Shell = [2, 6]
    Triad = [0, 2, 4]
    Seventh = [0, 2, 4, 6]
    Ninth = [0, 2, 4, 6, 8]
    Eleventh = [0, 2, 4, 6, 8, 10]
    Thirteenth = [0, 2, 4, 6, 8, 10, 12]


class Key:
    def __init__(self, key: Note, mode: Mode = Mode.Major):
        self.key = key
        self.mode = mode

        # find the intervals by rotating the ionian mode
        # intervals by the mode value
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

    def to_track(self, velocity=127, duration=1.0, tempo=180):
        return Track.from_notes([
            [note + (12 if note < self.key.value else 0)]
            for note in self.note_values + [self.key.value + 12]
        ], tempo=tempo, velocity=velocity, duration=duration)

    def chord(self, degree: int = 1, form: ChordForm = ChordForm.Shell):
        return [
            self.note_values[(i + degree - 1) % len(self.note_values)]
            for i in form.value
        ]

    @property
    def note_values(self):
        return [note.value for note in self.notes]