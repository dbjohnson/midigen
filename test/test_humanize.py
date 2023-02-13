from midigen import humanize
from midigen import rhythm


def test_pulse():
    assert [
        msg.velocity
        for msg in humanize.pulse(
            rhythm.four_on_the_floor(),
            even=True,
            ducking=1
        ).messages
        if msg.type == 'note_on'
    ] == [0, 127, 0, 127]

    assert [
        msg.velocity
        for msg in humanize.pulse(
            rhythm.four_on_the_floor(),
            even=False,
            ducking=1
        ).messages
        if msg.type == 'note_on'
    ] == [127, 0, 127, 0]

    assert [
        msg.velocity
        for msg in humanize.pulse(
            rhythm.straight_8ths(),
            even=True,
            ducking=1
        ).messages
        if msg.type == 'note_on'
    ] == [0, 37, 127, 37, 0, 37, 127, 37]
