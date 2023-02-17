import random
from typing import List
from itertools import permutations

from midigen.keys import Key, Note, Mode


class Node:
    def __init__(self, value: int = 0):
        self.value = value
        self.edges = []

    def add_edge(self, node: 'Node', weight: float = 1.0):
        self.edges.append(Edge(self, node, weight))

    def next(self):
        return random.choices(
            self.edges,
            weights=[edge.weight for edge in self.edges]
        )[0].node2


class Edge:
    def __init__(self, node1: Node, node2: Node, weight: float = 1.0):
        self.node1 = node1
        self.node2 = node2
        self.weight = weight


class Graph:
    def __init__(
        self,
        key: Key = Key(Note.C, Mode.Major),
        degrees: List[int] = list(range(1, 8)),
        octave_min: int = 2,
        octave_max: int = 4,
    ):
        self.key = key
        self.degrees = degrees
        self.octave_min = octave_min
        self.octave_max = octave_max
        self.nodes = [
            Node(self.key.note(degree).value_for_octave(octave))
            for octave in range(self.octave_min, self.octave_max + 1)
            for degree in self.degrees
        ]

        # connect all nodes with edges weighted by distance
        for n1, n2 in permutations(self.nodes, 2):
            weight = 1 / (abs(n1.value - n2.value) + 1)
            n1.add_edge(n2, weight)
            n2.add_edge(n1, weight)

        self.edges = [
            edge
            for note in self.nodes
            for edge in note.edges
        ]

    def clear_weights(self):
        for edge in self.edges:
            edge.weight = 0
        return self

    def strengthen_connections(self, pairs: List[Note], weight: float = 2.0):
        for n1, n2 in pairs:
            for edge in self.edges:
                if (
                    Note.from_value(edge.node1.value) == n1 and
                    Note.from_value(edge.node2.value) == n2 and
                    abs(edge.node1.value - edge.node2.value) <= 12
                ):
                    edge.weight += weight
        return self

    def generate_sequence(self, length: int = 16, start_note: int = None):
        start_node = next(
            (n for n in self.nodes if n.value == start_note),
            self.nodes[0]
        )
        sequence = [start_node]
        for _ in range(length - 1):
            sequence.append(sequence[-1].next())

        return [
            n.value for n in sequence
        ]

    def follow(self, other: List[int]):
        start_note = min(self.nodes, key=lambda n: abs(n.value - other[-1]))
        return self.generate_sequence(len(other), start_note.value)
