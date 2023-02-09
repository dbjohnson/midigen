"""
Enumerate the MIDI notes for the common
12-tone equal temperament scale starting at C0
"""
from enum import Enum


class Note(Enum):
    C = 60
    C_SHARP = 61
    Db = 61
    D = 62
    D_SHARP = 63
    Eb = 63
    E = 64
    F = 65
    F_SHARP = 66
    Gb = 66
    G = 67
    G_SHARP = 68
    Ab = 68
    A = 69
    A_SHARP = 70
    Bb = 70
    B = 71

    def __add__(self, offset: int):
        for note in Note:
            if (note.value) % 12 == (self.value + offset) % 12:
                return note

    def __sub__(self, offset: int):
        return self + (-offset)
