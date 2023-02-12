from pkg_resources import resource_stream


def _load_map(filename):
    with resource_stream("midigen", filename) as fh:
        return {
            key: int(value)
            for row in fh.read().decode().strip().split('\n')[1:]
            for (key, value) in [row.split(',')]
        }


DRUM_NOTES = _load_map("percussion_map.csv")
INSTRUMENTS = _load_map("instrument_map.csv")
