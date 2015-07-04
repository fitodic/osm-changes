#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
The script used for data extraction.
"""

from exportosm.reader import FeatureReader
from exportosm.utils import prepare_osm_id, check_bad_geom
from dbase.connection import engine, session, Base
from dbase.tables import Feature, OSMfile
from dbase.tables import GeomPoint, GeomLine, GeomMultiLine
from dbase.tables import GeomMultiPolygon, GeomOtherRelation
from dbase.entries import find_feature, find_file
from osgeo import gdal
from datetime import date
import argparse


def main(filename, osm_config_file):
    """ Reads the PBF file. """

    # required for OSM data format
    gdal.SetConfigOption('OGR_INTERLEAVED_READING', 'YES')

    # set 'OSM_CONFIG_fILE'
    gdal.SetConfigOption('OSM_CONFIG_FILE', osm_config_file)

    # extract file date
    filedate = ''.join([s for s in filename if s.isdigit()])
    creation_date = date(
        int(filedate[:4]), int(filedate[4:6]), int(filedate[6:8]))

    # find existing file
    existing_file = find_file(creation_date)
    # create new file
    if not existing_file:
        osmfile = OSMfile(creation_date)
        session.add(osmfile)
        session.flush()

    osmfile_id = find_file(creation_date).id

    lyr_read = FeatureReader(filename)

    for layer, feature in lyr_read.readData():

        # extract important attributes
        osm_id = prepare_osm_id(feature, layer)
        osm_version = feature.GetField('osm_version')
        osm_timestamp = feature.GetField('osm_timestamp')
        all_tags = feature.GetField('all_tags')
        geom = feature.GetGeometryRef()

        # detect corrupt geometries
        bad_geom = check_bad_geom(geom, osm_id)
        if bad_geom or bad_geom == 'BONKERS!':
            continue

        # find duplicate features
        duplicate = find_feature(osm_id, osm_version, osm_timestamp)

        # add new data
        if not duplicate:
            new_feature = Feature(osmfile_id, osm_id, osm_version,
                                  osm_timestamp, all_tags, layer)

            if layer == 'points':
                new_feature.point = GeomPoint(geom)
            elif layer == 'lines':
                new_feature.line = GeomLine(geom)
            elif layer == 'multilinestrings':
                new_feature.multiline = GeomMultiLine(geom)
            elif layer == 'multipolygons':
                new_feature.multipolygon = GeomMultiPolygon(geom)
            elif layer == 'other_relations':
                new_feature.other_rel = GeomOtherRelation(geom)

            session.add(new_feature)

        else:
            # reference it to the current file
            duplicate.file_id = osmfile_id

        session.flush()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Export OSM data')
    parser.add_argument('SRC', type=str, help='Name of the input OSM file')
    parser.add_argument('CONFIG', type=str, nargs='?',
                        default='./osm-changes/data/default_osmconf.ini', help='OSM config file (optional)')
    args = parser.parse_args()

    main(args.SRC, args.CONFIG)

    print 'Committing changes to DB.'
    session.commit()
    print 'Closing connection.'
    session.close()
