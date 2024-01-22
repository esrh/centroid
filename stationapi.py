import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, MultiPoint
from pyproj import Transformer
import settings

def find_center_station(station_list_str: str = '新宿、横浜', in_tokyo: bool =True) -> dict:
    for split_str in [',', ' ', '　', '、']:
        if split_str in station_list_str:
            station_list = station_list_str.split(split_str)
            break
    else:
        station_list = [station_list_str]
    if in_tokyo:
        stations = gpd.read_file('data/stations_within_tokyo.geojson', crs=4612).to_crs(2451)
    else:
        stations = gpd.read_file('data/stations.geojson', crs=4612).to_crs(2451)
    ans_stations = pd.DataFrame()
    for station in station_list:
        ans_stations = pd.concat([ans_stations, stations[stations.N02_005 == station].head(1)])
    ans_stations.loc[:, 'geometry'] = ans_stations.geometry.centroid
    hiningen_center = MultiPoint(ans_stations.geometry.to_list()).centroid
    transformer = Transformer.from_crs("EPSG:2451", "EPSG:4612", always_xy=True)
    transformed_longitude, transformed_latitude = transformer.transform(hiningen_center.x, hiningen_center.y)
    return dict(
        center_wkt=hiningen_center.wkt,
        center_4612_wkt=Point(transformed_longitude, transformed_latitude).wkt,
        station_name=stations.loc[stations.distance(hiningen_center).idxmin()].N02_005,
        stations_geojson=ans_stations.to_crs(4612).to_json()
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
    res = find_center_station(settings.sample_station_list, in_tokyo=True)
    # res = find_center_station('川崎、天王寺', in_tokyo=False)
    print(res.get('station_name'), res.get('center_4612_wkt'))

if __name__ == '__main__':
    main()

