from dbase.connection import session
from dbase.tables import Feature, OSMfile
from sqlalchemy import and_


def find_feature(osm_id, osm_version, osm_timestamp):
    """ Fetches the existing feature. """

    return session.query(Feature).filter(and_(
        Feature.osm_id == osm_id,
        Feature.osm_version == osm_version,
        Feature.osm_timestamp == osm_timestamp)).first()


def find_file(date):
    """ Fetches the existing file. """
    return session.query(OSMfile).filter(OSMfile.creation_date == date).first()
