from connection import session, Base
from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy import DateTime, Integer, Unicode, Date
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, backref
from geoalchemy2.types import Geometry
from geoalchemy2.shape import from_shape
from shapely.wkb import loads


class Feature(Base):
    __tablename__ = 'feature'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('osmfile.id'))
    osm_id = Column(Unicode)
    osm_version = Column(Integer)
    osm_timestamp = Column(DateTime(timezone=True))
    all_tags = Column(HSTORE)
    geom_type = Column(Unicode)

    osmfile = relationship("OSMfile", backref='feature')
    point = relationship("GeomPoint", uselist=False, backref='feature')
    line = relationship("GeomLine", uselist=False, backref='feature')
    multiline = relationship("GeomMultiLine", uselist=False, backref='feature')
    multipolygon = relationship(
        "GeomMultiPolygon", uselist=False, backref='feature')
    other_rel = relationship(
        "GeomOtherRelation", uselist=False, backref='feature')

    def __init__(self, file_id, osm_id, osm_version, osm_timestamp, all_tags, geom_type):
        self.file_id = file_id
        self.osm_id = osm_id
        self.osm_version = osm_version
        self.osm_timestamp = osm_timestamp
        self.all_tags = all_tags
        self.geom_type = geom_type


class OSMfile(Base):
    __tablename__ = 'osmfile'

    id = Column(Integer, primary_key=True)
    creation_date = Column(Date)

    def __init__(self, creation_date):
        self.creation_date = creation_date


class GeomPoint(Base):
    __tablename__ = 'geom_point'

    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'))
    the_geom = Column(Geometry('POINT', srid=4326))

    def __init__(self, geom):
        self.the_geom = from_shape(loads(geom.ExportToWkb()), srid=4326)


class GeomLine(Base):
    __tablename__ = 'geom_line'

    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'))
    the_geom = Column(Geometry('LINESTRING', srid=4326))

    def __init__(self, geom):
        self.the_geom = from_shape(loads(geom.ExportToWkb()), srid=4326)


class GeomMultiLine(Base):
    __tablename__ = 'geom_multiline'

    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'))
    the_geom = Column(Geometry('MULTILINESTRING', srid=4326))

    def __init__(self, geom):
        self.the_geom = from_shape(loads(geom.ExportToWkb()), srid=4326)


class GeomMultiPolygon(Base):
    __tablename__ = 'geom_multipolygon'

    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'))
    the_geom = Column(Geometry('MULTIPOLYGON', srid=4326))

    def __init__(self, geom):
        self.the_geom = from_shape(loads(geom.ExportToWkb()), srid=4326)


class GeomOtherRelation(Base):
    __tablename__ = 'geom_other_rel'

    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.id'))
    the_geom = Column(Geometry('GEOMETRYCOLLECTION', srid=4326))

    def __init__(self, geom):
        self.the_geom = from_shape(loads(geom.ExportToWkb()), srid=4326)


class JobOperation(Base):
    __tablename__ = 'job_operation'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job.id'), primary_key=True)
    operation_id = Column(
        Integer, ForeignKey('operation.id'), primary_key=True)
    parameters = Column(Unicode)

    operation = relationship("Operation", backref='job_operation')
    results = relationship("Result", backref='job_operation')

    def __init__(self, parameters):
        self.parameters = parameters


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

    operations = relationship("JobOperation", backref='job')

    def __init__(self, name):
        self.name = name


class Operation(Base):
    __tablename__ = 'operation'

    id = Column(Integer, primary_key=True)
    func_name = Column(Unicode)

    def __init__(self, func_name):
        self.func_name = func_name


class Result(Base):

    """
    For more info see:
    http://stackoverflow.com/questions/28331046/\
    why-does-sqlalchemy-initialize-hstore-field-as-null
    """

    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    job_operation_id = Column(Integer, ForeignKey('job_operation.id'))
    results = Column(MutableDict.as_mutable(HSTORE), default={})

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('results', {})
        super(Result, self).__init__(**kwargs)
