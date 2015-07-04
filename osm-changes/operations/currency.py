from dbase.connection import session
from dbase.tables import Feature, OSMfile
from general import time_boundary, convert_timestamp, save_result, current_data
from sqlalchemy import and_
from datetime import datetime


def currency_revision_needed(**kwargs):
    """ Marks features in need of revision. """

    # get current data
    features = current_data(**kwargs)

    # find the temporal boundary of the specified group of OSM features
    ts_boundary = time_boundary(**kwargs)

    for feature in features:

        # revision is not needed yet
        if convert_timestamp(feature.osm_timestamp) >= ts_boundary:
            result = 0

        # revision is needed
        else:
            result = 1

        # save results to the DB
        save_result(kwargs['job_op_id'], feature.osm_id, result)


def currency_coefficient(**kwargs):
    """ Assigns a currency coefficient to each feature. The larger the
    coefficient, the greater the need for updating the object. """

    # get current data
    features = current_data(**kwargs)

    # find the temporal boundary of the specified group of OSM features
    ts_boundary = time_boundary(**kwargs)

    for feature in features:
        # the result is the timestamp difference in days
        result = (ts_boundary - convert_timestamp(feature.osm_timestamp)).days

        # save results to the DB
        save_result(kwargs['job_op_id'], feature.osm_id, result)
