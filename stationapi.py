import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import unary_union
import contextily as cx
from pyproj import Transformer
import settings

def find_center_station(station_list_str : str) -> dict:
    for split_str in [',', ' ', '　', '、']:
        if split_str in station_list_str:
            hiningen_station_list = station_list_str.split(split_str)
            break
    else:
        hiningen_station_list = [station_list_str]
    stations = gpd.read_file(r'stations.geojson', crs=4612).to_crs(2451)
    hiningen_stations = stations[stations.N02_005.isin(hiningen_station_list)]
    hiningen_stations.loc[:, 'geometry'] = hiningen_stations.geometry.centroid
    hiningen_center = Point(hiningen_stations.unary_union.centroid)

    transformer = Transformer.from_crs("EPSG:2451", "EPSG:4612")
    transformed_longitude, transformed_latitude = transformer.transform(hiningen_center.x, hiningen_center.y)

    return dict(
        center_wkt=hiningen_center.wkt,
        center_4612_wkt=Point(transformed_longitude, transformed_latitude).wkt,
        station_name=stations.loc[stations.distance(hiningen_center).idxmin()].N02_005
    )

def main():
    res = find_center_station(settings.sample_station_list)
    print(res.get('station_name'))

if __name__ == '__main__':
    main()
