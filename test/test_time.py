from midigen.time import Measure, TimeSignature


def test_time_alignment():
    m1 = Measure(time_signature=TimeSignature(4, 4))
    m2 = Measure(time_signature=TimeSignature(16, 16))
    assert m2.duration_ticks == m1.duration_ticks * 4
