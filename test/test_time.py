from midigen.time import Measure, TimeSignature


def test_time_alignment():
    # make sure 16/16 and 4/4 are the same duration in time - but not in ticks!
    m1 = Measure(time_signature=TimeSignature(4, 4), tempo=30)
    m2 = Measure(time_signature=TimeSignature(16, 16), tempo=120)
    assert m1.duration_ticks != m2.duration_ticks
    assert m1.duration_secs == m2.duration_secs
