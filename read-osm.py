from geojson import Point, Feature, FeatureCollection, dumps
import osmiter

way_id = 154870255
osm_file = "./bj_11.osm"

features = osmiter.iter_from_osm(osm_file)
lst_node = []
for feature in features:
    if feature["type"] == "way" and feature["id"] == way_id:
        lst_node = feature["nd"]
        break

if len(lst_node):
    features = osmiter.iter_from_osm(osm_file)
    with open('./out.geojson', 'w') as w:
        lst_feature = []
        for feature in features:
            if feature["type"] == "node" and feature["id"] in lst_node:
                lst_feature.append(
                    Feature(geometry=Point(
                        tuple([feature['lon'], feature['lat']])),
                            properties={
                                'id': feature['id'],
                                'name': '西单北大街'
                            }))
        feature_collection = FeatureCollection(lst_feature)
        w.write('{}'.format(dumps(feature_collection, indent=4)))
