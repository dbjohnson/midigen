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

        self.beat_duration_secs = 60 / tempo
        self.beat_duration_ticks = int(second2tick(
            self.beat_duration_secs,
            TICKS_PER_BEAT,
            bpm2tempo(tempo)
        ))

        self.duration_secs = self.beat_duration_secs * time_signature.numerator
        self.duration_ticks = int(second2tick(
            self.duration_secs,
            TICKS_PER_BEAT,
            bpm2tempo(tempo)
        ))

    def mutate(self, msg_mutator: callable):
        return msg_mutator(self)

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

        template = Measure(
            time_signature=time_signature,
            tempo=tempo
        )

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
                        time=int(template.beat_duration_ticks * i * step)
                    ),
                    Message(
                        'note_off',
                        note=note,
                        velocity=velocity,
                        time=int(template.beat_duration_ticks * (i + duration) * step)
                    )
                ]
            ]
        )
