import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import unary_union
import contextily as cx
from pyproj import Transformer
import settings

def find_center_station(station_list_str: str, in_tokyo: bool =True) -> dict:
    for split_str in [',', ' ', '　', '、']:
        if split_str in station_list_str:
            hiningen_station_list = station_list_str.split(split_str)
            break
    else:
        hiningen_station_list = [station_list_str]
    if in_tokyo:
        stations = gpd.read_file('stations_within_tokyo.geojson', crs=4612).to_crs(2451)
    else:
        stations = gpd.read_file('stations.geojson', crs=4612).to_crs(2451)
    hiningen_stations = stations[stations.N02_005.isin(hiningen_station_list)]
    hiningen_stations.drop_duplicates(subset=['N02_005'], inplace=True)
    if len(hiningen_stations) < len(hiningen_station_list):
        stations = gpd.read_file('stations.geojson', crs=4612).to_crs(2451)
        hiningen_stations = stations[stations.N02_005.isin(hiningen_station_list)]
        hiningen_stations.drop_duplicates(subset=['N02_005'], inplace=True)
    hiningen_stations.loc[:, 'geometry'] = hiningen_stations.geometry.centroid
    hiningen_center = Point(hiningen_stations.unary_union.centroid)
    transformer = Transformer.from_crs("EPSG:2451", "EPSG:4612", always_xy=True)
    transformed_longitude, transformed_latitude = transformer.transform(hiningen_center.x, hiningen_center.y)
    return dict(
        center_wkt=hiningen_center.wkt,
        center_4612_wkt=Point(transformed_longitude, transformed_latitude).wkt,
        station_name=stations.loc[stations.distance(hiningen_center).idxmin()].N02_005,
        stations_geojson=hiningen_stations.to_crs(4612).to_json()
    )

def drop_duplicate_station(gdf):
    gdf['duplicate'] = False
    for index, row in gdf.iterrows():
        # 現在のジオメトリに対してバッファを適用し、100m以内の近隣を検索
        buffer = row.geometry.buffer(100)  # 100メートルのバッファ
        possible_matches_index = list(gdf.sindex.intersection(buffer.bounds))
        possible_matches = gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[
            possible_matches.intersects(buffer) & (possible_matches['my_column'] == row['my_column'])
        ]
        for pm_index in precise_matches.index:
            if pm_index != index:
                gdf.at[pm_index, 'duplicate'] = True
        # 重複フラグがTrueの行を削除
        gdf_filtered = gdf[~gdf['duplicate']].copy()
        # 'duplicate'列を削除
        gdf_filtered.drop(columns=['duplicate'], inplace=True)

def main():
    res = find_center_station(settings.sample_station_list)
    # res = find_center_station('川崎、天王寺')
    print(res.get('station_name'))

if __name__ == '__main__':
    main()

