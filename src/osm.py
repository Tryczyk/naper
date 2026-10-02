import osmium

from constants import (
    MAP_LAYERS,
    OSM_FILE_PATH,
)
from utils import save_geojson

import osmium

class CombinedRoadsFilter(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.all_roads = []
        self.speed_gt_50 = []
        self.traffic_calming = []
        self.traffic_signals = []
        self.buildings = []
        self.bodies_of_water = []
        self.dirt_roads = []
        
        self.car_highway_types = {
            'motorway', 'motorway_link', 'trunk', 'trunk_link',
            'primary', 'primary_link', 'secondary', 'secondary_link',
            'tertiary', 'tertiary_link', 'unclassified', 'residential', 
            'living_street'
        }
        
        self.dirt_highway_types = {'track', 'path'}
        self.dirt_surfaces = {'dirt', 'earth', 'ground', 'sand', 'mud'}

    def node(self, n):
        tags = dict(n.tags)
        highway = tags.get("highway")
        traffic_calming = tags.get("traffic_calming") 
        
        if traffic_calming:
            try:
                self.traffic_calming.append(self._create_point_feature(n, tags))
            except osmium.InvalidLocationError:
                pass
                
        if highway == "traffic_signals":
            try:
                self.traffic_signals.append(self._create_point_feature(n, tags))
            except osmium.InvalidLocationError:
                pass

    def way(self, w):
        tags = dict(w.tags)
        highway = tags.get("highway")
        traffic_calming = tags.get("traffic_calming")
        building = tags.get("building")
        natural = tags.get("natural")
        waterway = tags.get("waterway")
        
        if not highway and not traffic_calming and not building and not natural and not waterway:
            return
            
        coords = []
        for n in w.nodes:
            try:
                coords.append([n.lon, n.lat])
            except osmium.InvalidLocationError:
                pass
                
        if len(coords) < 2:
            return
            
        feature = self._create_linestring_feature(coords, tags)

        if highway in self.car_highway_types:
            self.all_roads.append(feature)

        maxspeed = tags.get("maxspeed")
        if maxspeed:
            try:
                speed_val = int(''.join(filter(str.isdigit, maxspeed)))
                if speed_val > 50:
                    self.speed_gt_50.append(feature)
            except ValueError:
                pass

        if traffic_calming:
            self.traffic_calming.append(feature)

        if building:
            self.buildings.append(feature)

        if natural == "water" or waterway:
            self.bodies_of_water.append(feature)

        surface = tags.get("surface")
        if highway in self.dirt_highway_types or surface in self.dirt_surfaces:
            self.dirt_roads.append(feature)

    def _create_point_feature(self, n, tags):
        return {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [n.location.lon, n.location.lat]},
            "properties": tags
        }
        
    def _create_linestring_feature(self, coords, tags):
        return {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": tags
        }


def create_geojson_files(osm_file_path=OSM_FILE_PATH):
    layers = {
        name: layer["path"]
        for name, layer in MAP_LAYERS.items()
        if name != "driven"
    }

    if all(path.exists() for path in layers.values()):
        return

    print("Missing GeoJSON files. Starting the extraction process...")
    handler = CombinedRoadsFilter()
    handler.apply_file(str(osm_file_path), locations=True)

    features = {
        "all_roads": handler.all_roads,
        "speed_gt_50": handler.speed_gt_50,
        "traffic_calming": handler.traffic_calming,
        "traffic_lights": handler.traffic_signals,
        "buildings": handler.buildings,
        "bodies_of_water": handler.bodies_of_water,
        "dirt_roads": handler.dirt_roads,
    }
    for name, path in layers.items():
        save_geojson(path, features[name])


