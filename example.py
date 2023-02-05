import mido
from midiro.keys import Key, Mode, ChordForm
from midiro.note import Note
from midiro.sequencer import Sequence, Track


port = mido.open_output('midiro', virtual=True)

Key(Note.A, Mode.Major).to_track().play(port)

Sequence([
    Key(Note.A, Mode.Major).to_track(),
    Key(Note.C, Mode.Aeolian).to_track()
]).play(port)

Track.from_notes([
    Key(Note.C).chord(degree, ChordForm.Seventh)
    for i, degree in enumerate([2, 5, 1, 6, 2, 5, 1])
], tempo=90).play(port)