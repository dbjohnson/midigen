from typing import List
from enum import Enum

from mido import Message, second2tick, bpm2tempo


TICKS_PER_BEAT = 1000


class NoteLength(Enum):
    Whole = 1
    Half = 2
    Quarter = 4
    Eighth = 8
    Sixteenth = 16
    ThirtySecond = 32
    SixtyFourth = 64
    HundredTwentyEighth = 128


class TimeSignature:
    def __init__(
        self,
        numerator: int = 4,
        denominator: NoteLength = NoteLength.Quarter
    ):
        self.numerator = numerator
        self.denominator = denominator


class Measure:
    def __init__(
        self,
        time_signature: TimeSignature = TimeSignature(4, NoteLength.Quarter),
        tempo: float = 120,
        messages: List[Message] = []
    ):
        self.time_signature = time_signature
        self.tempo = tempo
        self.messages = messages
        self.duration_ticks = int(second2tick(
            60 / tempo * time_signature.numerator,
            TICKS_PER_BEAT,
            bpm2tempo(tempo)
        ))

    @staticmethod
    def from_pattern(
        pattern: List[List[int]],
        time_signature: TimeSignature = TimeSignature(4, NoteLength.Quarter),
        tempo: float = 120,
        velocity: int = 127,
        duration: float = 0.99,
    ):
        """
        Generate a one measure sequence of notes; the pattern
        is a list of notes to play at each beat
        """
        assert len(pattern) == time_signature.numerator

        return Measure(
            time_signature=time_signature,
            tempo=tempo,
            messages=[
                msg
                for i, notes in enumerate(pattern)
                if notes
                for note in notes
                for msg in [
                    Message(
                        'note_on',
                        note=note,
                        velocity=velocity,
                        time=int(second2tick(
                            60 / tempo * i,
                            TICKS_PER_BEAT,
                            bpm2tempo(tempo)
                        ))
                    ),
                    Message(
                        'note_off',
                        note=note,
                        velocity=velocity,
                        time=int(second2tick(
                            60 / tempo * (i + duration),
                            TICKS_PER_BEAT,
                            bpm2tempo(tempo)
                        ))
                    )
                ]
            ]
        )
