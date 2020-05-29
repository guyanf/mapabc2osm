import time
from dbconn import db_conn, cursor
import pdb


def create_temp_tab(conn, tab_road, tab_temp_node):

    sql_create = """drop TABLE if EXISTS {0};
    SELECT gid as line_gid,(pt).path[1] as ptindex,(pt).geom as geom,
    name_chn as name, road_class, form_way, direction, uid into {0}
    FROM (SELECT gid, ST_DumpPoints(geom) AS pt, name_chn, road_class,
    form_way, direction, gid as uid FROM {1} where bz=1) as foo ;
    alter table {0} add column gid serial4 primary key;
    create index idx_{0}_line_gid on {0} using btree(line_gid);
    create index idx_{0}_ptindex on {0} using btree(ptindex);
    create index idx_{0}_geom on {0} using gist(geom);
    """.format(tab_temp_node, tab_road)

    cursor(conn, sql_create, commit=True)


def create_node(conn, tab_road, tab_temp_node, tab_node):

    sql_create_tab = """drop table if exists {0};
    create table {0} (gid serial4 primary key, line_id int4, name varchar(160),
    node_index int4, node_type varchar(2), node_id int4, road_class int4,
    form_way int2, direction int2, uid int8,
    geom geometry(Point,4326), wkt varchar(200))
    ;""".format(tab_node)
    cursor(conn, sql_create_tab, commit=True)

    sql_line_gid = "select line_gid, min(ptindex), max(ptindex) from {0}" \
        " group by line_gid;".format(tab_temp_node)
    rows_line_gid = cursor(conn, sql_line_gid, ret=True)
    for row_line_gid in rows_line_gid:
        line_gid, mmin, mmax = row_line_gid
        print(line_gid, mmin, mmax)
        if mmax - mmin >= 2:
            sql_insert = """insert into {4}(line_id, node_index, node_type,
            node_id, geom, wkt, road_class, form_way, direction, name, uid)
            select line_gid, ptindex, '', gid, geom, st_astext(geom),
            road_class, form_way, direction, name, uid
            from {0} where line_gid = {1} and ptindex between {2} and {3};
            """.format(tab_temp_node, line_gid, mmin + 1, mmax - 1, tab_node)
            cursor(conn, sql_insert)
            # pdb.set_trace()

        for mm in (mmin, mmax):
            sql_insert_se = """insert into {3}(line_id, node_index, node_type,
            node_id, geom, wkt, road_class, form_way, direction, name, uid)
            select t1.line_gid, t1.ptindex, t1.node_type, t2.gid, t2.geom,
            st_astext(t2.geom), t1.road_class, t1.form_way, t1.direction,
            t1.name, t1.uid from
            (select line_gid, ptindex, 'se' as node_type, geom, road_class,
            form_way, direction, name, uid from {0}
            where line_gid = {1} and ptindex = {2}) t1
            left join {0} t2 on st_dwithin(t1.geom, t2.geom, 0.0000001)
            order by t2.gid limit 1;
            """.format(tab_temp_node, line_gid, mm, tab_node)
            cursor(conn, sql_insert_se)

    conn.commit()

    sql_update = "update {} set name = '' where name is null;".format(tab_node)
    cursor(conn, sql_update, commit=True)


def main():

    print('go', time.strftime('%H:%M:%S', time.localtime(time.time())))
    dct_db = {
        'host': '192.168.11.229',
        'port': 5432,
        'user': 'postgres',
        'pw': 'Mapabc&2016',
        'db': 'routing'
    }
    tab_road = 'roadsegment'
    tab_temp_node = 'tab_node_guf'
    tab_node = 'roadnode_osm'

    conn = db_conn(dct_db['host'], dct_db['port'], dct_db['user'],
                   dct_db['pw'], dct_db['db'])

    create_temp_tab(conn, tab_road, tab_temp_node)
    create_node(conn, tab_road, tab_temp_node, tab_node)
    print('over', time.strftime('%H:%M:%S', time.localtime(time.time())))


if __name__ == "__main__":
    main()
