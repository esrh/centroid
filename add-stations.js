


function addStations(map, geoJsonString) {
  let blueIcon = L.icon({
    iconUrl: 'blue-marker.png', // 青い丸のアイコン画像ファイルを指定
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  
  L.geoJSON(geojsonFeature, {
    pointToLayer: function(feature, latlng) {
        return L.marker(latlng, { icon: blueIcon });
    }
  }).addTo(map);
}