"""
Helper functions / examples for basic rhyhm patterns
"""
from typing import List
from pkg_resources import resource_stream

from midigen.time import TimeSignature, Measure


with resource_stream("midigen", "percussion_map.csv") as fh:
    NOTES = {
        key: int(value)
        for row in fh.read().decode().strip().split('\n')[1:]
        for (key, value) in [row.split(',')]
    }


def measure(
    pattern: List[List[int]],
    tempo: float = 90,
    velocity: int = 127,
    time_signature: TimeSignature = TimeSignature(4, 4)
):
    return Measure.from_pattern(
        pattern=pattern,
        time_signature=time_signature,
        tempo=tempo,
        velocity=velocity,
    )


def four_on_the_floor(
    click=[NOTES['Kick Drum']],
    tempo=90,
    velocity=127
):
    return measure([click, None, None, None] * 4, tempo=tempo, velocity=velocity)


def straight_16ths(
    click=[NOTES['Hi-Hat Closed']],
    tempo=90,
    velocity=127
):
    return measure([click, None] * 8, tempo=tempo, velocity=velocity)


def straight_8ths(
    click=[NOTES['Ride Cymbal']],
    tempo=90,
    velocity=127
):
    return measure([click] * 16, tempo=tempo, velocity=velocity)


def son_clave(
    click=[NOTES['Floor Tom 1']],
    tempo=90,
    velocity=127
):
    return measure([
        click, None, None, click,
        None, None, click, None,
        None, None, click, None,
        click, None, None, None
    ], tempo=tempo, velocity=velocity)


def rumba_clave(
    click=[NOTES['Floor Tom 1']],
    tempo=90,
    velocity=127
):
    return measure([
        click, None, None, click,
        None, None, None, click,
        None, None, click, None,
        click, None, None, None
    ], tempo=tempo, velocity=velocity)


def brushes(
    click=[NOTES['Snare Cross Stick']],
    tempo=90,
    velocity=40
):
    return measure([
        click, None, None, click,
        click, None, None, click,
        click, None, None, click,
        click, None, None, click,
    ], tempo=tempo, velocity=velocity)
