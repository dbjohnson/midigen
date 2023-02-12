import random
from midigen.time import Measure


def add_swing(measure: Measure, swing: float = 0.1):
    shift = int(swing * measure.beat_duration_ticks)

    def swung_beat(time):
        beat_frac = (time % measure.beat_duration_ticks) / measure.beat_duration_ticks
        return max(0, int(time + beat_frac * shift))

    return Measure(
        measure.time_signature,
        measure.tempo,
        [
            msg.copy(time=swung_beat(msg.time))
            for msg in measure.messages
        ],
    )


def randomize(measure: Measure, beat_frac: float = 0.01):
    def randomized(time):
        return max(
            0,
            int(time + random.normalvariate(0, beat_frac) * measure.beat_duration_ticks)
        )

    return Measure(
        measure.time_signature,
        measure.tempo,
        [
            msg.copy(time=randomized(msg.time))
            for msg in measure.messages
        ],
    )


if __name__ == '__main__':
    import mido
    from midigen import rhythm
    from midigen.sequencer import Track

    port = mido.open_output('midigen', virtual=True)

    Track.from_measures([randomize(add_swing(
        rhythm.straight_8ths(tempo=60),
        0.2
    ))
        for _ in range(5)
    ]).play(port)

    m1 = rhythm.straight_8ths()
    m2 = add_swing(m1, 0.5)
    print([msg.time for msg in m1.messages if msg.type == 'note_on'])
    print([msg.time for msg in m2.messages if msg.type == 'note_on'])
