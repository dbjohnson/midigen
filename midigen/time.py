from typing import List

from mido import Message


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
        messages: List[Message] = []
    ):
        self.time_signature = time_signature
        self.messages = messages
        self.duration_ticks = TICKS_PER_BEAT * time_signature.numerator

    def mutate(self, msg_mutator: callable):
        return msg_mutator(self)

    @staticmethod
    def from_pattern(
        pattern: List[List[int]],
        time_signature: TimeSignature = TimeSignature(4, 4),
        velocity: int = 127,
        duration: float = 0.5,
    ):
        """
        Generate a one measure sequence of notes; the pattern
        is a list of notes to play at each beat
        """
        # ensure pattern is a multiple of the time signature
        assert len(pattern) % time_signature.numerator == 0
        step = time_signature.numerator / len(pattern) * TICKS_PER_BEAT

        return Measure(
            time_signature=time_signature,
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
                        time=int(i * step)
                    ),
                    Message(
                        'note_off',
                        note=note,
                        velocity=velocity,
                        time=int((i + duration) * step)
                    )
                ]
            ]
        )
