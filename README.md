# midigen
[![License](https://img.shields.io/github/license/dbjohnson/midigen.svg)]()
[![PyPi](https://img.shields.io/pypi/v/midigen.svg)](https://pypi.python.org/pypi/midigen)
![GHA](https://github.com/dbjohnson/midigen/actions/workflows/tests.yml/badge.svg)


Python library for generating simple chord progression midi files

[demo](https://dbjohnson.github.io/midigen/)

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
from midigen.sequencer import Song, Track


# open new midi port via mido
port = mido.open_output('midigen', virtual=True)

# play C minor scale
Key(Note.C, Mode.Minor).to_track().play(port)

# make a simple ii V I vi chord progression in the key of C
key = Key(Note.C, Mode.Major)
time_signature = TimeSignature(4, 4)
tempo = 90
progression = [2, 5, 1, 6]

chords = Track.from_measures([
    Measure.from_pattern(
        pattern=[
            key.relative_key(degree).chord(
                # default chords are the base triad - try adding extensions
                extensions=[7],
                # pick a voicing close to the root triad
                match_voicing=key.triad()
            )
        ] * time_signature.numerator,
        time_signature=time_signature,
        velocity=90
    )
    for degree in progression
])

# play to port
chords.play(port, tempo=tempo)

# write the song to a MIDI file
Song([chords]).to_midi('midigen.mid', tempo=tempo)
```
