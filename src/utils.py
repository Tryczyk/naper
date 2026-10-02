import json

def any_none(arguments):
    for element in arguments:
        if element is None:
            return True
    return False

def count_lines(filepath):
    with open(filepath, 'rb') as f:
        bufgen = iter(lambda: f.read(1024 * 1024), b'')
        return sum(buf.count(b'\n') for buf in bufgen)

def save_geojson(filename, features):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)
