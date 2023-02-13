import random
from math import sin, cos, pi
from midigen.time import Measure, TICKS_PER_BEAT


def swing(measure: Measure, swing: float = 0.1):
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


def randomize_time(measure: Measure, beat_frac: float = 0.001):
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


def randomize_velocity(measure: Measure, frac: float = 0.01):
    def randomized(msg):
        return min(
            127,
            max(
                0,
                int(msg.velocity + random.normalvariate(0, frac * 127))
            )
        )

    return Measure(
        measure.time_signature,
        [
            msg.copy(velocity=randomized(msg))
            for msg in measure.messages
        ],
    )


def pulse(measure: Measure, even: bool = True, ducking: float = 0.2):
    def pulsed(msg):
        beat, frac = divmod(msg.time, TICKS_PER_BEAT)
        frac /= TICKS_PER_BEAT
        if frac > 0.5:
            frac = 1 - frac
            beat += 1

        off_beat = (beat % 2 == 0) == even
        if off_beat:
            # full attenuation for on the off beats;
            return int(msg.velocity * (1 - ducking * cos(frac * pi / 2)))
        else:
            # no attenuation for "on" beats
            # the higher the frac, the further we are from the "on" beat,
            # the more we attenuate
            return int(msg.velocity * (1 - ducking * sin(frac * pi / 2)))

    return Measure(
        measure.time_signature,
        [
            msg.copy(velocity=pulsed(msg))
            for msg in measure.messages
        ],
    )
