# midigen
[![License](https://img.shields.io/github/license/dbjohnson/midigen.svg)]()
[![PyPi](https://img.shields.io/pypi/v/midigen.svg)](https://pypi.python.org/pypi/midigen)
![GHA](https://github.com/dbjohnson/midigen/actions/workflows/tests.yml/badge.svg)


Python library for generating simple chord progression midi files

## Installation
```cmd
pip install midigen
```

## Example usage
### Command line

Play a `ii-V-I-vi` pattern in the key of `G`; loop it four times 
```cmd
midigen --key G --chords ii V I vi  --loop 4 --play
```

### Python


```python
import mido
from midigen.notes import Note
from midigen.keys import Key, Mode
from midigen.time import TimeSignature, Measure
from midigen.sequencer import Song, Track, play_notes


port = mido.open_output('midigen', virtual=True)

# C major scale
Key(Note.C, Mode.Major).to_track().play(port)

# A simple chord progression
key = Key(Note.C, Mode.Major)
time_signature = TimeSignature(4, 4)
tempo = 90
progression = [2, 5, 1, 6]

chords = Track.from_measures([
    Measure.from_pattern(
        pattern=[
            key.relative_key(degree).chord(
                [7],
                # pick a voicing close to the root triad
                match_voicing=key.triad()
            )
        ] * time_signature.numerator,
        time_signature=time_signature,
        velocity=90
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
        velocity=80
    )
    for degree in progression
], name='melody')
melody.play(port)

# Stack the melody and chords in a single track
chords.stack(melody).play(port)

# Or use the Song class to play multiple tracks
Song([chords, melody]).play(port)

# Write the song to a MIDI file
Song([chords, melody]).to_midi('example.mid')
```
