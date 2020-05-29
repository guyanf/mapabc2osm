from nose.tools import *
import unittest
import tempfile
import os
from contextlib import contextmanager
from datetime import datetime
from collections import OrderedDict
import logging
import sys

import osmium


@contextmanager
def WriteExpect(expected):
    # fname = tempfile.mktemp(dir=tempfile.gettempdir(), suffix='.opl')
    fname = './aaa.osm'
    writer = osmium.SimpleWriter(fname)
    try:
        yield writer
    finally:
        writer.close()


class OBJECT(object):
    def __init__(self, **params):
        for k, v in params.items():
            print(k, v)
            setattr(self, k, v)


class NodeWriter(osmium.SimpleHandler):
    def __init__(self, writer):
        osmium.SimpleHandler.__init__(self)
        self.writer = writer

    def node(self, n):
        self.writer.add_node(n)


class TestWriteWay(unittest.TestCase):
    def test_node_list(self):
        with WriteExpect('w0 v0 dV c0 t i0 u T Nn1,n2,n3,n-4') as w:
            w.add_way(OBJECT(nodes=(1, 2, 3, -4)))

    def test_node_list_none(self):
        with WriteExpect('w0 v0 dV c0 t i0 u T N') as w:
            w.add_way(OBJECT(nodes=None))


class TestWriteRelation(unittest.TestCase):
    def test_relation_members(self):
        with WriteExpect('r0 v0 dV c0 t i0 u T Mn34@foo,r200@,w1111@x') as w:
            w.add_relation(
                OBJECT(members=(('n', 34, 'foo'), ('r', 200, ''), ('w', 1111,
                                                                   'x'))))

    def test_relation_members_None(self):
        with WriteExpect('r0 v0 dV c0 t i0 u T M') as w:
            w.add_relation(OBJECT(members=None))


def main():

    aa = OBJECT(members=(('n', 34, 'foo'), ('r', 200, ''), ('w', 1111, 'x')))
    print(aa)


if __name__ == '__main__':
    main()
