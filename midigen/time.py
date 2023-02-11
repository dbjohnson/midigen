from typing import List

from mido import Message, second2tick, bpm2tempo


TICKS_PER_BEAT = 480


class TimeSignature:
    def __init__(
        self,
        numerator: int = 4,
        denominator: int = 4
    ):
        self.numerator = numerator
        self.denominator = denominator


class Measure:
    def __init__(
        self,
        time_signature: TimeSignature = TimeSignature(4, 4),
        tempo: float = 120,
        messages: List[Message] = []
    ):
        self.time_signature = time_signature
        self.tempo = tempo
        self.messages = messages
        self.duration_secs = 60 / self.tempo * time_signature.numerator
        self.duration_ticks = int(second2tick(
            self.duration_secs,
            TICKS_PER_BEAT,
            bpm2tempo(tempo)
        ))

    @staticmethod
    def from_pattern(
        pattern: List[List[int]],
        time_signature: TimeSignature = TimeSignature(4, 4),
        tempo: float = 120,
        velocity: int = 127,
        duration: float = 0.99,
    ):
        """
        Generate a one measure sequence of notes; the pattern
        is a list of notes to play at each beat
        """
        # ensure pattern is a multiple of the time signature
        assert len(pattern) % time_signature.numerator == 0
        step = time_signature.numerator / len(pattern)

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
                            60 / tempo * i * step,
                            TICKS_PER_BEAT,
                            bpm2tempo(tempo)
                        ))
                    ),
                    Message(
                        'note_off',
                        note=note,
                        velocity=velocity,
                        time=int(second2tick(
                            60 / tempo * (i + duration) * step,
                            TICKS_PER_BEAT,
                            bpm2tempo(tempo)
                        ))
                    )
                ]
            ]
        )
