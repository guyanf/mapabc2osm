"""
Converts a file from one format to another.

This example shows how to write objects to a file.
"""

import osmium as o
import os
import pdb


class Convert(o.SimpleHandler):
    def __init__(self, writer):
        super(Convert, self).__init__()
        self.writer = writer

    def node(self, n):
        self.writer.add_node(n)

    def way(self, w):
        self.writer.add_way(w)

    def relation(self, r):
        self.writer.add_relation(r)


if __name__ == '__main__':

    in_osm = './test.osm'
    out_osm = './new_test.osm'

    if os.path.isfile(out_osm):
        os.remove(out_osm)

    writer = o.SimpleWriter(out_osm)
    handler = Convert(writer)

    handler.apply_file(in_osm)

    writer.close()
