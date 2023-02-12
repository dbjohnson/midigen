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
    velocity: int = 127,
    time_signature: TimeSignature = TimeSignature(4, 4)
):
    return Measure.from_pattern(
        pattern=pattern,
        time_signature=time_signature,
        velocity=velocity,
        duration=0.1
    )


def four_on_the_floor(
    click=[NOTES['Kick Drum']],
    velocity=127
):
    return measure([click, None, None, None] * 4, velocity=velocity)


def straight_8ths(
    click=[NOTES['Hi-Hat Closed']],
    velocity=127
):
    return measure([click, None] * 8, velocity=velocity)


def straight_16ths(
    click=[NOTES['Hi-Hat Closed']],
    velocity=127
):
    return measure([click] * 16, velocity=velocity)


def son_clave(
    click=[NOTES['Floor Tom 1']],
    velocity=127
):
    return measure([
        click, None, None, click,
        None, None, click, None,
        None, None, click, None,
        click, None, None, None
    ], velocity=velocity)


def rumba_clave(
    click=[NOTES['Floor Tom 1']],
    velocity=127
):
    return measure([
        click, None, None, click,
        None, None, None, click,
        None, None, click, None,
        click, None, None, None
    ], velocity=velocity)


def brushes(
    click=[NOTES['Snare Cross Stick']],
    velocity=40
):
    return measure([
        click, None, None, click,
        click, None, None, click,
        click, None, None, click,
        click, None, None, click,
    ], velocity=velocity)
