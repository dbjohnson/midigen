from enum import Enum

from midigen.sequencer import Track
from midigen.notes import Note
from midigen.time import Measure, TimeSignature, NoteLength


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


class ChordForm(Enum):
    Shell = [3, 7]
    Triad = [1, 3, 5]
    Seventh = [1, 3, 5, 7]
    Ninth = [1, 3, 5, 7, 9]
    Eleventh = [1, 3, 5, 7, 9, 11]
    Thirteenth = [1, 3, 5, 7, 9, 11, 13]


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
            key + sum(self.intervals[:i])
            for i in range(len(self.intervals))
        ]

        self.note_values = [
            note.value + (12 if note.value < self.key.value else 0)
            for note in self.notes
        ]

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
                    for note in self.note_values + [self.key.value + 12]
                ],
                time_signature=TimeSignature(8, NoteLength.Quarter),
                tempo=tempo,
                velocity=velocity,
                duration=duration
            )
        ])

    def chord(
        self,
        degree: int = 1,
        form: ChordForm = ChordForm.Shell
    ):
        """
        Generate a chord from the key
        For example, a basic triad for the C major chord would be:
        Key(Note.C).chord(1, ChordForm.Triad)
        """
        return [
            self.note_values[(i - 1 + degree - 1) % len(self.note_values)]
            for i in form.value
        ]
