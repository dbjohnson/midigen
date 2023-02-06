import mido
from midiro.keys import Key, Mode, ChordForm
from midiro.note import Note
from midiro.sequencer import Song, Track
from midiro.time import TimeSignature, NoteLength, Measure


port = mido.open_output('midiro', virtual=True)

# A major scale
Key(Note.A, Mode.Major).to_track(tempo=200).play(port)


# Simple sequence with two scales played together
Song([
    Key(Note.A, Mode.Major).to_track(),
    Key(Note.C, Mode.Aeolian).to_track()
]).play(port)


# A simple chord progression
key = Key(Note.C)
time_signature = TimeSignature(4, NoteLength.Quarter)
tempo = 90
progression = [2, 5, 1, 6]

chords = Track.from_measures([
    Measure.from_pattern(
        pattern=[
            key.chord(degree, ChordForm.Shell)
        ] * time_signature.numerator,
        time_signature=time_signature,
        tempo=tempo,
        velocity=50
    )
    for degree in progression
], name='chords')
chords.play(port)

# A simple melody
melody = Track.from_measures([
    Measure.from_pattern(
        pattern=[
            [key.note(degree).value],
            [key.note(degree + 2).value],
            [key.note(degree + 5).value],
            None
        ],
        time_signature=time_signature,
        tempo=tempo,
        velocity=80
    )
    for degree in progression
], name='melody')
melody.play(port)

# Stack the melody and chords in a single track
chords.stack(melody).play(port)

# Or use the Sequence class to play multiple tracks
Song([chords, melody]).play(port)

# Write the song to a MIDI file
Song([chords, melody]).to_midi('example.mid')