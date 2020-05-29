#!/usr/bin/evn python
# --coding:utf-8---
# brief: connect db & execute sql
# author: thomas
# date: 2016.8.1
# org:  mapabc.com

from __future__ import print_function
from __future__ import division

import psycopg2
import psycopg2.extras


def cursor(conn, sql, commit=False, ret=False):
    cursor1 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor1.execute(sql)
    if commit:
        conn.commit()
    if ret:
        return cursor1.fetchall()


def db_conn(host, port, user, pw, db):

    try:
        conn = psycopg2.connect(host=host, port=port, user=user,
                                password=pw, database=db)
    except Exception as e:
        print (e.args[0])
        return

    return conn


def main():

    conn = db_conn('127.0.0.1', '5432', 'postgres', '', 'postgis')
    conn.close()


if __name__ == '__main__':
    main()