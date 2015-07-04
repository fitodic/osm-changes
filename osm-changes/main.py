#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
The main script used for detecting and evaluating changes in OSM data.

Useful links:
http://stackoverflow.com/questions/15206010/\
    how-to-pass-on-argparse-argument-to-function-as-kwargs
"""

from dbase.connection import session
from dbase.tables import Feature, OSMfile, Job, Operation, JobOperation, Result
from operations.geojson import create_GeoJSON
import operations.counters
import operations.changes
import operations.currency
import operations.geometry
import argparse


def main(**kwargs):

    # create a new job
    job = Job(kwargs['new_job'])

    for key in kwargs:
        # find operations
        if key[:3] == 'op_':

            # check for an existing operation
            existing_operation = session.query(Operation).filter(
                Operation.func_name == key[3:]).first()

            # define JobOperation parameters
            job_oper = JobOperation(';'.join([str(kwargs[a]) for a in kwargs
                                              if kwargs[a] != True]))

            # define new operation
            if not existing_operation:
                job_oper.operation = Operation(key[3:])
            # use existing operation
            else:
                job_oper.operation = existing_operation

            # add job and operatios to DB
            job.operations.append(job_oper)
            session.add_all([job, job_oper])
            session.flush()

    for assoc in job.operations:
        # ignore output function
        if assoc.operation.func_name != 'geojson':

            # initialize counter functions
            if assoc.operation.func_name[:5] == 'count':
                operation = getattr(operations.counters,
                                    assoc.operation.func_name)

            # initialize change functions
            elif assoc.operation.func_name[:6] == 'change':
                operation = getattr(operations.changes,
                                    assoc.operation.func_name)

            # initialize currency functions
            elif assoc.operation.func_name[:8] == 'currency':
                operation = getattr(operations.currency,
                                    assoc.operation.func_name)

            # initialize geometry functions
            elif assoc.operation.func_name[:4] == 'geom':
                operation = getattr(operations.geometry,
                                    assoc.operation.func_name)

            # test the existence of a tag of interest (TOI)
            try:
                operation(
                    job_op_id=assoc.id,
                    fkey=kwargs['fkey'],
                    fvalue=kwargs['fvalue'],
                    osm_version=kwargs['osm_version'],
                    tag_of_interest=kwargs['tag_of_interest'])

            except KeyError:
                operation(
                    job_op_id=assoc.id,
                    fkey=kwargs['fkey'],
                    fvalue=kwargs['fvalue'],
                    osm_version=kwargs['osm_version'])

            session.flush()

    # create a GeoJSON output file
    if kwargs['op_geojson']:
        create_GeoJSON(job, kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='OSM Changes',
                                     description='Analyze changes in OSM features')

    parser.add_argument('new_job', type=str,
                        help='Enter the name of the new job')

    parser.add_argument('fkey', type=str, default='amenity',
                        help='Enter feature key (e.g. amenity)')

    parser.add_argument('fvalue', type=str, default='atm',
                        help='Enter feature value (e.g. atm)')

    parser.add_argument('osm_version', type=int, default=1,
                        help='Enter the min acceptable version of an OSM feature (default: 1)')

    parser.add_argument('-toi', '--tag-of-interest', required=False,
                        nargs='?', default=argparse.SUPPRESS,
                        help='Enter tag of interest (e.g. name)')

    parser.add_argument('-ogj', '--op-geojson', required=True,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Outputs results into a GEOJSON file (EPSG:4326)')

    parser.add_argument('-oci', '--op-count-inserts', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Counts how many new tags were added')

    parser.add_argument('-ocu', '--op-count-updates', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Counts how many tags were updated')

    parser.add_argument('-ocd', '--op-count-deletions', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Counts how many tags were deleted')

    parser.add_argument('-ocg', '--op-count-geom-changes', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Counts changes in geometries')

    parser.add_argument('-ocjw', '--op-change-jaro-winkler', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Use the Jaro-Winkler algorithm to detect the level of change')

    parser.add_argument('-ocl', '--op-change-levenshtein', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Use Levenshtein distance to detect the level of change')

    parser.add_argument('-ocrn', '--op-currency-revision-needed',
                        required=False, default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Find objects in need for revision (out-of-date)')

    parser.add_argument('-occ', '--op-currency-coefficient', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Calculate the currency coefficient for each OSM feature')

    parser.add_argument('-ogfo', '--op-geom-from-original', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Calculate the distance from the original position (nodes)')

    parser.add_argument('-ogsd', '--op-geom-sum-dist', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Calculate cumulative distance across points (nodes)')

    parser.add_argument('-ogad', '--op-geom-area-diffs', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Calculate the difference in areas (closed ways)')

    parser.add_argument('-ogld', '--op-geom-length-diffs', required=False,
                        default=argparse.SUPPRESS, nargs='?', const=True,
                        help='Calculate the difference in lengths (ways)')

    args = parser.parse_args()

    main(**vars(args))

    print 'Committing data and closing connection.'
    session.flush()
    session.commit()
    session.close()
