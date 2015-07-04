from dbase.connection import session
from dbase.tables import Feature, Result, OSMfile
from datetime import datetime
from sqlalchemy import and_
from geoalchemy2.shape import to_shape


def current_data(**kwargs):
    """ Get current data from the Feature table. """

    # find the ID of the latest file
    latest_file = session.query(OSMfile).order_by(
        OSMfile.creation_date).all()[-1]

    # get current features (features from the last file)
    list_current = session.query(Feature).filter(and_(
        Feature.all_tags[kwargs['fkey']] == kwargs['fvalue']),
        Feature.file_id == latest_file.id,
        Feature.osm_version >= kwargs['osm_version']).order_by(
        Feature.osm_version).all()

    return list_current


def save_result(job_operation_id, osm_id, value):
    """ Save the result into an Hstore.
    For more info visit: http://stackoverflow.com/questions/28331046/\
    why-does-sqlalchemy-initialize-hstore-field-as-null """

    # checks the existence of the job->operation combination
    exists = session.query(Result).filter(
        Result.job_operation_id == job_operation_id).first()

    # saves new results
    if not exists:
        new_result = Result()
        new_result.job_operation_id = job_operation_id
        new_result.results[osm_id] = str(value)

        session.add(new_result)

    # updates existing results
    else:
        exists.results[osm_id] = str(value)

    session.flush()


def time_boundary(**kwargs):
    """ Sets the time boundary between up-to-date features and outdated
    features. """

    # find the ID of the latest file
    latest_file = session.query(OSMfile).order_by(OSMfile.id).all()[-1]

    # get current features (features from the last file)
    features = session.query(Feature).filter(and_(
        Feature.all_tags[kwargs['fkey']] == kwargs['fvalue']),
        Feature.file_id == latest_file.id).order_by(
        Feature.osm_timestamp).all()

    # find the index of the median timestamp
    idx = int(len(features) / 2)

    return convert_timestamp(features[idx].osm_timestamp)


def convert_timestamp(timestamp):
    """ Convert SQLalchemy's DateTime to Python's datetime. """

    new_ts = datetime(timestamp.year, timestamp.month, timestamp.day,
                      timestamp.hour, timestamp.minute)

    return new_ts


def find_geom(feature):
    """ Locates the feature's geometry. """

    if feature.geom_type == 'points':
        return to_shape(feature.point.the_geom)
    elif feature.geom_type == 'lines':
        return to_shape(feature.line.the_geom)
    elif feature.geom_type == 'multilinestrings':
        return to_shape(feature.multiline.the_geom)
    elif feature.geom_type == 'multipolygons':
        return to_shape(feature.multipolygon.the_geom)
    elif feature.geom_type == 'other_relations':
        return to_shape(feature.other_rel.the_geom)
