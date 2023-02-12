import random
from midigen.time import Measure, TICKS_PER_BEAT


def add_swing(measure: Measure, swing: float = 0.1):
    shift = int(swing * TICKS_PER_BEAT)

    def swung_beat(msg):
        beat_frac = (msg.time % TICKS_PER_BEAT) / TICKS_PER_BEAT
        return max(0, int(msg.time + beat_frac * shift))

    return Measure(
        measure.time_signature,
        [
            msg.copy(time=swung_beat(msg))
            for msg in measure.messages
        ],
    )


def randomize(measure: Measure, beat_frac: float = 0.01):
    def randomized(msg):
        return max(
            0,
            int(msg.time + random.normalvariate(0, beat_frac * TICKS_PER_BEAT))
        )

    return Measure(
        measure.time_signature,
        [
            msg.copy(time=randomized(msg))
            for msg in measure.messages
        ],
    )
