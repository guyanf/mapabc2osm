import time
import xml.etree.ElementTree as ET
import pandas as pd
from osmwriter import OSMWriter
from six import StringIO
from dbconn import db_conn, cursor
import pdb


def create_node(xml, conn, tab_node, user, visible, version, changeset,
                cur_time):

    print('create node...')
    sql_node = """select node_id, st_x(wkt::geometry), st_y(wkt::geometry),
    array_agg(node_type) from {}
    group by node_id, wkt;""".format(tab_node)
    rows_node = cursor(conn, sql_node, ret=True)
    for row_node in rows_node:
        node_id, lon, lat, node_type = row_node
        node_type = tuple(set(node_type))
        n_type = {}
        if node_type[0] == '' and len(node_type) == 1:
            n_type = {}
        elif node_type[0] == 'se' and len(node_type) == 1:
            n_type = {'osm_type': 'end'}
        elif '' in node_type and 'se' in node_type and len(node_type) == 2:
            n_type = {'osm_type': 'end & node'}

        tag = n_type
        # print(node_id, lat, lon, n_type)
        xml.node(node_id, lat, lon, tag)
        # ,
        #          version=version,
        #          timestamp=cur_time,
        #          changeset=changeset,
        #          visible=visible,
        #          user=user)
    return xml


def create_way(xml, conn, tab_node, user, visible, version, changeset,
               cur_time):

    print('create way...')
    dct_rc = {
        'motorway': ((41000, 41000), (1, 2, 15, 7, 17)),
        'trunk': ((42000, 43000), (1, 2, 15, 7, 17)),
        'primary': ((44000, 51000), (1, 2, 15, 7, 17)),
        'secondray': ((45000, 52000), (1, 2, 15, 7, 17)),
        'tertiary': ((47000, 53000), (1, 2, 15, 7, 17)),
        'unclassified': ((54000, 54000), (1, 2, 15)),
        'residential': ((49, 49), (1, 2, 15)),
        'motorway_link': ((41000, 41000), (3, 8, 53, 56)),
        'trunk_link': ((42000, 43000, 44000, 51000), (3, 5, 6, 8, 53, 56)),
        'primary_link': ((52000, 47000, 53000, 54000), (3, 5, 6, 8, 53, 56)),
        'secondary_link':
        ((42000, 44000, 45000, 51000, 52000), (9, 10, 13, 14, 16, 11, 12)),
        'tertiary_link':
        ((47000, 53000, 54000, 49), (9, 10, 13, 14, 16, 11, 12))
    }

    lst_tag_name = [
        'id', 'name', 'highway', 'road_class', 'form_way', 'direction', 'uid',
        'oneway'
    ]

    lst = []
    for k, v in dct_rc.items():
        lst.append(
            """when road_class in {} and form_way in {} then '{}'""".format(
                v[0], v[1], k))

    field = " case {} else 'unclassified' end way_type ".format('\n'.join(lst))
    del lst

    sql_way = """select line_id, name, node_index, node_id, {1}, road_class::varchar,
    form_way::varchar, direction::varchar, uid,
    (case when direction=2 then 'yes' when direction=3 then '-1' else '' end)
     as oneway from {0};
    """.format(tab_node, field)
    df = pd.read_sql(sql_way, conn)
    # print(df)
    df.fillna('')
    df.loc[df['direction'] == '4', 'way_type'] == 'footway'

    df_way = df.groupby([
        'line_id', 'name', 'way_type', 'road_class', 'form_way', 'direction',
        'uid', 'oneway'
    ]).groups
    # print(df_way)

    ii = 1
    total = len(df_way.keys())
    for key in df_way.keys():
        if ii % 1000 == 0:
            print('{}/{}'.format(ii, total))
        ii += 1
        dct_tags = dict(zip(lst_tag_name, key))

        lst_node = df.loc[df['line_id'] == dct_tags['id']].sort_values(
            ['node_index'])['node_id'].tolist()

        tags = {}
        for kk, vv in dct_tags.items():
            # print(kk, vv)
            if kk not in ('id', 'uid') and vv != '':
                tags[kk] = vv

        xml.way(dct_tags['id'], tags, lst_node, uid=dct_tags['uid'])
        # ,
        # version=version,
        # timestamp=cur_time,
        # changeset=changeset,
        # visible=visible,
        # user=user)
        # xml.way(100, {'pub': 'yes'}, [1, 2])

    del df
    del df_way

    return xml


def create_relation(xml, cur_time):

    xml.relation(1, {'type': 'boundary'}, [('node', 1), ('way', 100, 'outer')])

    return xml


def create_osm(conn, tab_node, osm_file, user, visible, version, changeset,
               cur_time):

    sql_box = "SELECT ST_Extent(geom) FROM {};".format(tab_node)
    bbox = [
        float(ii)
        for ii in cursor(conn, sql_box, ret=True)[0][0][4:-1].replace(
            ',', ' ').split(' ')
    ]

    string = StringIO()
    xml = OSMWriter(fp=string)

    xml.bounds(bbox)
    xml = create_node(xml, conn, tab_node, user, visible, version, changeset,
                      cur_time)
    xml = create_way(xml, conn, tab_node, user, visible, version, changeset,
                     cur_time)

    # xml = create_relation(xml, cur_time)
    xml.close(close_file=False)
    output = ET.tostring(ET.fromstring(string.getvalue()))
    head = bytes('<?xml version="1.0" encoding="UTF-8"?>\n', 'utf-8')

    output = head + output

    with open(osm_file, 'wb') as w:
        w.write(output)


def main():

    dct_db = {
        'host': '192.168.11.229',
        'port': 5432,
        'user': 'postgres',
        'pw': 'Mapabc&2016',
        'db': 'routing'
    }
    tab_node = 'roadnode_osm'
    osm_file = './test.osm'

    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    user = 'Thomas Chen'
    visible = True
    version = 20200522
    changeset = 1

    conn = db_conn(dct_db['host'], dct_db['port'], dct_db['user'],
                   dct_db['pw'], dct_db['db'])

    create_osm(conn, tab_node, osm_file, user, visible, version, changeset,
               cur_time)
    conn.close()


if __name__ == '__main__':
    main()
