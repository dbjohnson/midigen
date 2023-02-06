import time
from threading import Thread
from typing import List

from mido import Message, MetaMessage, MidiFile, MidiTrack
from mido import bpm2tempo, tick2second
from mido.ports import BaseOutput

from midiro.time import Measure, TICKS_PER_BEAT


class Track:
    def __init__(
        self,
        duration_ticks: int,
        messages: List[Message] = [],
        meta_messages: List[MetaMessage] = [],
    ):
        self.duration_ticks = duration_ticks
        self.messages = messages
        self.meta_messages = meta_messages

    @staticmethod
    def from_measures(measures: List[Measure], name: str = 'midiro'):
        t = Track(0, [])
        for measure in measures:
            t = t.append(Track(
                measure.duration_ticks,
                measure.messages,
                [
                    MetaMessage(
                        'time_signature',
                        numerator=measure.time_signature.numerator,
                        denominator=measure.time_signature.denominator.value,
                        time=measure.messages[0].time
                    ),
                    MetaMessage(
                        'set_tempo',
                        tempo=int(bpm2tempo(measure.tempo)),
                        time=measure.messages[0].time
                    ),
                    MetaMessage(
                        'track_name',
                        name=name
                    )
                ]
            ))
        return t

    def play(self, port: BaseOutput):
        def play():
            tstart = time.time()
            for msg in self.messages:
                current_tempo = max([
                    m for m in self.meta_messages
                    if m.type == 'set_tempo' and
                    m.time <= msg.time
                ],
                    key=lambda m: m.time
                ).tempo

                msg_time_secs = tick2second(
                    msg.time,
                    TICKS_PER_BEAT,
                    current_tempo
                )
                while (dt := msg_time_secs - (time.time() - tstart)) > 0:
                    time.sleep(dt)

                port.send(msg)

        Thread(target=play).start()

    def shift_time(self, offs_ticks: int):
        return Track(
            duration_ticks=self.duration_ticks,
            messages=[
                Message(
                    msg.type,
                    note=msg.note,
                    velocity=msg.velocity,
                    time=msg.time + offs_ticks
                )
                for msg in self.messages
            ],
            meta_messages=[
                MetaMessage(**{
                    **msg.dict(),
                    'time': msg.time + offs_ticks
                })
                for msg in self.meta_messages
            ]
        )

    def shift_pitch(self, offs: int):
        return Track(
            duration=self.duration,
            messages=[
                Message(
                    msg.type,
                    note=msg.note + offs,
                    velocity=msg.velocity,
                    time=msg.time
                )
                for msg in self.messages
            ],
            meta_messages=self.meta_messages
        )

    def append(self, other: 'Track'):
        shifted = other.shift_time(self.duration_ticks)
        return Track(
            self.duration_ticks + other.duration_ticks,
            self.messages + shifted.messages,
            self.meta_messages + shifted.meta_messages
        )

    def stack(self, other: 'Track'):
        return Track(
            max(self.duration_ticks, other.duration_ticks),
            self.messages + other.messages,
            self.meta_messages + other.meta_messages
        )

    def to_midi_track(self):
        track = MidiTrack()
        for msg in sorted(
            self.messages + self.meta_messages,
            key=lambda msg: msg.time
        ):
            track.append(msg)

        return track

    def to_midi(self, name: str):
        Song([self]).to_midi(name)


class Song:
    def __init__(self, tracks: List[Track] = []):
        self.tracks = tracks

    def play(self, port: BaseOutput):
        for track in self.tracks:
            track.play(port)

    def to_midi(self, name: str):
        mid = MidiFile()
        for track in self.tracks:
            mid.tracks.append(track.to_midi_track())
        mid.save(name)
