import time
from threading import Thread
from typing import List

from mido import Message, MetaMessage, MidiFile, MidiTrack
from mido import tick2second, bpm2tempo
from mido.ports import BaseOutput

from midigen.time import Measure, TimeSignature, TICKS_PER_BEAT


class Track:
    def __init__(
        self,
        name: str = 'midigen',
        duration_ticks: int = 0,
        messages: List[Message] = [],
        channel: int = 0,
        program: int = 0
    ):
        self.name = name
        self.duration_ticks = duration_ticks
        self.messages = sorted(messages, key=lambda m: m.time)
        self.channel = channel
        self.program = program

    @staticmethod
    def from_measures(
        measures: List[Measure],
        channel: int = 0,
        program: int = 0,
        name: str = 'midigen',
        stack: bool = False
    ):
        t = Track(name=name, channel=channel, program=program)
        for measure in measures:
            merge_method = t.stack if stack else t.append
            t = merge_method(Track(
                name,
                measure.duration_ticks,
                measure.messages,
                channel,
                program
            ))
        return t

    def play(self, port: BaseOutput, tempo: int = 90, block: bool = False):
        def play():
            tstart = time.time()
            for msg in self.messages:
                msg_time_secs = tick2second(
                    msg.time,
                    TICKS_PER_BEAT,
                    bpm2tempo(tempo)
                )
                while (dt := msg_time_secs - (time.time() - tstart)) > 0:
                    time.sleep(dt)

                port.send(msg.copy(channel=self.channel))

        t = Thread(target=play)
        t.start()
        if block:
            t.join()

    def shift_time(self, offs_ticks: int):
        return Track(
            name=self.name,
            duration_ticks=self.duration_ticks,
            messages=[
                msg.copy(time=msg.time + offs_ticks)
                for msg in self.messages
            ],
            channel=self.channel,
            program=self.program
        )

    def shift_pitch(self, offs: int):
        return Track(
            name=self.name,
            duration_ticks=self.duration_ticks,
            messages=[
                msg.copy(note=msg.note + offs)
                for msg in self.messages
            ],
            channel=self.channel,
            program=self.program
        )

    def append(self, other: 'Track'):
        shifted = other.shift_time(self.duration_ticks)
        return Track(
            self.name,
            self.duration_ticks + other.duration_ticks,
            self.messages + shifted.messages,
            channel=self.channel,
            program=self.program
        )

    def stack(self, other: 'Track'):
        return Track(
            self.name,
            max(self.duration_ticks, other.duration_ticks),
            self.messages + other.messages,
            channel=self.channel,
            program=self.program
        )

    def loop(self, n: int):
        return Track.string_tracks([self] * n)

    @staticmethod
    def string_tracks(tracks: List['Track']):
        t = tracks[0]
        for track in tracks[1:]:
            t = t.append(track)

        return t

    def to_midi_track(self):
        track = MidiTrack()
        track.append(MetaMessage('track_name', name=self.name))
        track.append(Message(
            'program_change',
            channel=self.channel,
            program=self.program
        ))
        sorted_msgs = sorted(
            [m.copy(channel=self.channel) for m in self.messages],
            key=lambda msg: msg.time
        )
        # convert timestamps to deltas
        tlast = sorted_msgs[0].time
        for msg in sorted_msgs:
            # make sure swing or other randomization hasn't moved notes out of bounds
            if 0 <= msg.time <= self.duration_ticks:
                track.append(
                    msg.copy(
                        time=msg.time - tlast
                    )
                )
                tlast = msg.time

        track.append(MetaMessage('end_of_track', time=self.duration_ticks - tlast))
        return track

    def to_midi(self, name: str):
        Song([self]).to_midi(name)


class Song:
    def __init__(self, tracks: List[Track] = []):
        self.tracks = tracks

    def play(self, port: BaseOutput, tempo: int = 90, block: bool = True):
        for i, track in enumerate(self.tracks):
            track.play(port)

        if block:
            time.sleep(max([
                tick2second(
                    t.duration_ticks,
                    TICKS_PER_BEAT,
                    bpm2tempo(tempo)
                )
                for t in self.tracks
            ]))

    def loop(self, n: int):
        return Song([t.loop(n) for t in self.tracks])

    def to_midi(
        self,
        name: str = 'midigen',
        tempo: int = 90,
        time_signature: TimeSignature = TimeSignature(4, 4)
    ):
        mid = MidiFile()
        mid.tracks.append(MidiTrack([
            MetaMessage('track_name', name=name),
            MetaMessage('set_tempo', tempo=bpm2tempo(tempo)),
            MetaMessage(
                'time_signature',
                numerator=time_signature.numerator,
                denominator=time_signature.denominator
            )
        ]))

        for track in sorted(self.tracks, key=lambda t: t.channel):
            mid.tracks.append(track.to_midi_track())
        mid.save(name)


def play_notes(notes, port, spacing_secs: int = 0, velocity: int = 90):
    """
    Simple function to play a list of notes on a given port.
    """
    for note in notes:
        port.send(Message(
            'note_on',
            note=note,
            velocity=velocity
        ))

        time.sleep(max(0.5, spacing_secs / 2))

        port.send(Message(
            'note_off',
            note=note,
        ))

        time.sleep(spacing_secs / 2)
