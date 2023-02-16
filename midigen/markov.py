import random
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
        )[0].node


class Edge:
    def __init__(self, node1: Node, node2: Node, weight: float = 1.0):
        self.node1 = node1
        self.node = node2
        self.weight = weight


class Graph:
    def __init__(
        self,
        key: Key = Key(Note.C, Mode.Major),
        octave_min: int = 1,
        octave_max: int = 5
    ):
        self.key = key
        self.octave_min = octave_min
        self.octave_max = octave_max
        self.nodes = [
            Node(note.value_for_octave(octave))
            for octave in range(self.octave_min, self.octave_max + 1)
            for note in self.key.notes
        ]

    def connect_all(self):
        for n1, n2 in permutations(self.nodes, 2):
            # weight edges by distance
            weight = 1 / (abs(n1.value - n2.value) + 1)
            n1.add_edge(n2, weight)
            n2.add_edge(n1, weight)
        return self

    def generate_sequence(self, length: int = 16, start_node: Node = None):
        sequence = [start_node or random.choice(self.nodes)]
        for _ in range(length - 1):
            sequence.append(sequence[-1].next())
        return [
            n.value for n in sequence
        ]
