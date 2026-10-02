from constants import MAP_DIR_PATH
from map import create_map
from osm import create_geojson_files
from parser import parse_data

def main(map_dir_path = MAP_DIR_PATH):
    map_dir_path.mkdir(parents=True, exist_ok=True)

    create_geojson_files()
    
    parse_data()

    create_map()


if __name__ == "__main__":
    main()

