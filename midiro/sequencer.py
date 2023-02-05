import time
from threading import Thread
from typing import List
from mido import Message
from mido.ports import BaseOutput
from midiro.note import Note


class Track:
    def __init__(self, notes: List[Message] = []):
        self.notes = notes

    def from_notes(
        notegroups: List[List[Note]],
        velocity=127,
        duration=1.0,
        tempo=180
    ):
        return Track([
            msg
            for i, notegroup in enumerate(notegroups)
            for note in notegroup
            for msg in [
                Message(
                    'note_on',
                    note=note,
                    velocity=velocity,
                    time=i * 60 / tempo
                ),
                Message(
                    'note_off',
                    note=note,
                    velocity=velocity,
                    time=(i + duration) * 60 / tempo
                )
            ]
        ])

    def play(self, port: BaseOutput):
        def play():
            sorted_notes = sorted(self.notes, key=lambda note: note.time)
            tstart = time.time()
            for note in sorted_notes:
                dt = note.time - (time.time() - tstart)
                if dt > 0:
                    time.sleep(dt)
                port.send(note)

        Thread(target=play).start()


class Sequence:
    def __init__(self, tracks: List[Track] = []):
        self.tracks = tracks

    def play(self, port: BaseOutput):
        for track in self.tracks:
            track.play(port)