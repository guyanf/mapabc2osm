import time
from geojson import LineString, Feature, Point, FeatureCollection, dumps, loads
from pyroutelib3 import Router  # Import the router
import pdb


def route(mode, osm_file, in_start_end, out_json):

    try:
        print('s', time.strftime('%H:%M:%S', time.localtime(time.time())))
        router = Router(mode, osm_file)  # Initialise it
        with open(out_json, 'w') as w:
            f = open(in_start_end, 'r')
            features = loads(f.read())
            x1, y1, x2, y2 = 0, 0, 0, 0
            for feat in features['features']:
                # print(feat['geometry']['coordinates'])
                if feat['properties']['s_e'] == 's':
                    x1, y1 = feat['geometry']['coordinates']
                if feat['properties']['s_e'] == 'e':
                    x2, y2 = feat['geometry']['coordinates']

            start = router.findNode(y1, x1)
            end = router.findNode(y2, x2)

            status, route = router.doRoute(
                start, end)  # Find the route - a list of OSM nodes

            if status == 'success':
                routeLatLons = list(map(router.nodeLatLon, route))

                my_feature = Feature(geometry=LineString(
                    tuple([i[::-1] for i in routeLatLons])))
                feature_collection = FeatureCollection([my_feature])

                # print(feature_collection)
                w.write('{}'.format(dumps(feature_collection, indent=4)))
        print('e', time.strftime('%H:%M:%S', time.localtime(time.time())))
        print('-' * 40)
    except Exception:
        pass

    finally:
        del router


def main():
    osm_file = './test.osm'
    out_json = '/home/chentonglei/Desktop/wkt/abc.geojson'
    in_start_end = '/home/chentonglei/Desktop/wkt/in_start_end.geojson'
    mode = 'car'
    route(mode, osm_file, in_start_end, out_json)


if __name__ == "__main__":
    main()
