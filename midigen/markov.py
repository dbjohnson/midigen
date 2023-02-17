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
        min_note: int = Note.C.value_for_octave(0),
        max_note: int = Note.C.value_for_octave(6),
        edge_weights: List[float] = None,
        degrees: List[int] = list(range(1, 8)),
    ):
        self.key = key
        self.degrees = degrees
        self.min_note = min_note
        self.max_note = max_note
        self.nodes = [
            Node(note_value)
            for octave in range(6)
            for degree in self.degrees
            for note_value in [self.key.note(degree).value_for_octave(octave)]
            if min_note <= note_value <= max_note
        ]

        # connect all nodes with edges weighted by distance
        for i, (n1, n2) in enumerate(permutations(self.nodes, 2)):
            if edge_weights:
                weight = edge_weights[i]
            else:
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

    def sequences_for_keys(
        self,
        keys: List[Key],
        notes_per_key: int = 8,
    ):
        def graph_for_key(key: Key):
            return Graph(
                key,
                self.min_note,
                self.max_note,
                degrees=self.degrees,
                edge_weights=[e.weight for e in self.edges]
            )

        s = [graph_for_key(keys[0]).generate_sequence(notes_per_key)]
        for key in keys[1:]:
            s.append(graph_for_key(key).follow(s[-1]))

        return s
