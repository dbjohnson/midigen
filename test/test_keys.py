from midigen.keys import Key, Mode
from midigen.notes import Note


def test_c_major_key():
    assert Key(Note.C, Mode.Major).notes == [
        Note.C, Note.D, Note.E, Note.F, Note.G, Note.A, Note.B
    ]


def test_c_minor_key():
    assert Key(Note.C, Mode.Aeolian).notes == [
        Note.C, Note.D, Note.D_SHARP, Note.F,
        Note.G, Note.G_SHARP, Note.A_SHARP
    ]


def test_c_major_chord():
    assert Key(Note.C, Mode.Major).triad() == [
        Note.C.value, Note.E.value, Note.G.value
    ]


def test_CV7():
    assert Key(Note.C, Mode.Mixolydian).chord([7]) == [
        Note.C.value, Note.E.value, Note.G.value, Note.Bb.value
    ]


def test_em9():
    assert Key(Note.E, Mode.Minor).chord([9]) == [
        Note.E.value, Note.G.value, Note.B.value,
        Note.F_SHARP.value + 12
    ]


def test_em9_1st_inv():
    assert Key(Note.E, Mode.Minor).chord([9], inversion=1) == [
        Note.G.value - 12, Note.B.value - 12,
        Note.F_SHARP.value, Note.E.value + 12,
    ]


def test_cmaj_rel_minor():
    assert Key(Note.C, Mode.Major).relative_key(6) == Key(Note.A, Mode.Aeolian)


def test_voicing():
    key = Key(Note.C, Mode.Major)
    prev = key.triad()
    prev
    assert key.chord([], match_voicing=prev) == prev
    assert key.chord([7], match_voicing=prev) == prev + [59]
