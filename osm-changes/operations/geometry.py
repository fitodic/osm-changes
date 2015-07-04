from dbase.tables import session
from dbase.tables import Feature, OSMfile, GeomMultiPolygon, GeomLine, GeomMultiLine, GeomPoint
from general import save_result, current_data
from geoalchemy2 import func


def geom_from_original(**kwargs):
    """ Calculates the distance from the first point.
    Function requires at least two points. """

    list_current = current_data(**kwargs)

    for current in list_current:

        if current.geom_type == 'points':

            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            if len(features) < 2:
                result = '0'

            else:
                geog1 = session.query(func.ST_GeogFromText(func.ST_AsText(
                    GeomPoint.the_geom))).filter(
                    GeomPoint.feature_id == features[0].id).first()[0]
                geog2 = session.query(func.ST_GeogFromText(func.ST_AsText(
                    GeomPoint.the_geom))).filter(
                    GeomPoint.feature_id == features[-1].id).first()[0]
                result = session.query(
                    func.ST_Distance(geog1, geog2, True)).first()[0]

            save_result(kwargs['job_op_id'], current.osm_id, str(result))


def geom_sum_dist(**kwargs):
    """ Calculates the cumulative distance accross points.
    Function requires at least three points. """

    list_current = current_data(**kwargs)

    for current in list_current:

        if current.geom_type == 'points':

            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            result = 0.0

            if len(features) >= 3:
                for i, feature in enumerate(features):

                    if i != 0:
                        geog1 = session.query(func.ST_GeogFromText(
                            func.ST_AsText(GeomPoint.the_geom))).filter(
                            GeomPoint.feature_id == features[i - 1].id).first()[0]
                        geog2 = session.query(func.ST_GeogFromText(
                            func.ST_AsText(GeomPoint.the_geom))).filter(
                            GeomPoint.feature_id == feature.id).first()[0]

                        result += session.query(func.ST_Distance(
                            geog1, geog2, True)).first()[0]

            save_result(kwargs['job_op_id'], current.osm_id, result)


def geom_area_diffs(**kwargs):
    """ Calculates the spatial difference between the first and the last
    version of the same area. Function requires at least two areas. """

    list_current = current_data(**kwargs)

    for current in list_current:

        if current.geom_type == 'multipolygons':

            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            if len(features) < 2:
                result = str(0.0)

            else:

                area1 = session.query(func.ST_Area(func.ST_GeogFromText(
                    func.ST_AsText(GeomMultiPolygon.the_geom)))).filter(
                        GeomMultiPolygon.feature_id == features[0].id).first()[0]

                area2 = session.query(func.ST_Area(func.ST_GeogFromText(
                    func.ST_AsText(GeomMultiPolygon.the_geom)))).filter(
                        GeomMultiPolygon.feature_id == features[1].id).first()[0]

                result = str(area2 - area1)

            save_result(kwargs['job_op_id'], current.osm_id, result)


def geom_length_diffs(**kwargs):
    """ Calculates the spatial difference between the first and the last
    version of the same line. Function requires at least two lines. """

    list_current = current_data(**kwargs)

    for current in list_current:

        if (current.geom_type == 'lines'
                or current.geom_type == 'multilinestrings'):

            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            if len(features) < 2:
                result = str(0.0)

            else:
                if current.geom_type == 'lines':
                    length1 = session.query(func.ST_Length(func.ST_GeogFromText(
                        func.ST_AsText(GeomLine.the_geom)))).filter(
                            GeomLine.feature_id == features[0].id).first()[0]

                    length2 = session.query(func.ST_Length(func.ST_GeogFromText(
                        func.ST_AsText(GeomLine.the_geom)))).filter(
                            GeomLine.feature_id == features[1].id).first()[0]

                else:
                    length1 = session.query(func.ST_Length(func.ST_GeogFromText(
                        func.ST_AsText(GeomMultiLine.the_geom)))).filter(
                            GeomMultiLine.feature_id == features[0].id).first()[0]

                    length2 = session.query(func.ST_Length(func.ST_GeogFromText(
                        func.ST_AsText(GeomMultiLine.the_geom)))).filter(
                            GeomMultiLine.feature_id == features[1].id).first()[0]

                result = str(length2 - length1)

            save_result(kwargs['job_op_id'], current.osm_id, result)
