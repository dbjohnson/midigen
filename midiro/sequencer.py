import time


class Sequencer:
    def play(self, port, notes, tempo=120):
        for note in notes:
            port.send(note)
            time.sleep(60 / tempo)
