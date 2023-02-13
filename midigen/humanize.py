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


def randomize_time(measure: Measure, beat_frac: float = 0.01):
    """
    Randomize time; on/off message pairs must be shifted by the same amount
    """
    on_msgs = [msg for msg in measure.messages if msg.type == 'note_on']
    off_msgs = [msg for msg in measure.messages if msg.type == 'note_off']
    other_messages = [msg for msg in measure.messages if msg not in on_msgs + off_msgs]

    randomized = []
    for on_msg in on_msgs:
        offs = int(random.normalvariate(0, beat_frac * TICKS_PER_BEAT))
        randomized.append(
            on_msg.copy(time=max(0, on_msg.time + offs))
        )
        try:
            matched_off = next(
                off_msg
                for off_msg in off_msgs
                if off_msg.note == on_msg.note and off_msg.time >= on_msg.time
            )
            randomized.append(
                matched_off.copy(time=max(0, matched_off.time + offs))
            )
        except StopIteration:
            pass

    return Measure(
        measure.time_signature,
        sorted(randomized + other_messages, key=lambda msg: msg.time)
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


def pulse(measure: Measure, even: bool = True, ducking: float = 0.1):
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
