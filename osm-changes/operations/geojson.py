"""
For more info see:
https://pcjericks.github.io/py-gdalogr-cookbook/index.html#
"""

from dbase.tables import session
from dbase.tables import Feature, OSMfile
from osgeo import ogr, osr
from geoalchemy2.shape import to_shape
from shapely.geometry import Point, LineString, MultiLineString, MultiPolygon
from shapely.geometry import GeometryCollection
from sqlalchemy import and_
from general import current_data
import os


def delete_file(path, filename):
    """ Delete existing file. """

    driver = ogr.GetDriverByName('GeoJSON')
    if os.path.exists(os.path.join(path, filename)):
        driver.DeleteDataSource(os.path.join(path, filename))


def create_GeoJSON(job, kwargs):
    """ Create GeoJSON file and fill it with processed features. """

    # relative output path
    path = './osm-changes/output/'
    # initialize datasource
    datasource = None

    # get current features
    features = current_data(**kwargs)

    for feature in features:

        # initialize escape message
        message = None

        # create the main dictionary with essential data
        fdata = {
            'osm_id': feature.osm_id,
            'osm_timestamp': str(feature.osm_timestamp),
            'osm_version': str(feature.osm_version),
            'feature_count': str(len(session.query(Feature).filter(
                Feature.osm_id == feature.osm_id).all())),
            'all_tags': str(feature.all_tags)
        }

        # create operation fields
        for association in job.operations:
            # avoid output function
            if association.operation.func_name != u'geojson':
                # create field name from function name
                try:
                    field_name = '%s_%s' % (
                        association.operation.func_name,
                        kwargs['tag_of_interest'])
                except KeyError:
                    field_name = str(association.operation.func_name)

                # get results for Job->Operation combination
                hstore_result = association.results[0].results

                # find osm_id (key) in results
                if hstore_result.has_key(feature.osm_id):
                    fdata[field_name] = hstore_result[feature.osm_id]
                else:
                    # implemented due to feature types with multiple geometries
                    if 'change_' not in field_name:
                        fdata[field_name] = 'None'
                    # implemented due to features without TOIs (JW and LD)
                    else:
                        message = 'skip feature'

        # move immediately to the next feature
        if message != None:
            continue

        # define output file
        if not datasource:
            filename = '%s_%s_%s.geojson' % (
                kwargs['fkey'], kwargs['fvalue'],
                kwargs['new_job'])
            delete_file(path, filename)
            datasource = define_GeoJSON(path, filename, fdata)

        # write this feature
        # depends on its geometry
        if feature.geom_type == 'points':
            write_feature(datasource, fdata, feature.point.the_geom)

        elif feature.geom_type == 'lines':
            write_feature(datasource, fdata, feature.line.the_geom)

        elif feature.geom_type == 'multilinestrings':
            write_feature(datasource, fdata, feature.multiline.the_geom)

        elif feature.geom_type == 'multipolygons':
            write_feature(datasource, fdata, feature.multipolygon.the_geom)

        elif feature.geom_type == 'other_relations':
            write_feature(datasource, fdata, feature.other_rel.the_geom)


def define_GeoJSON(path, filename, fdata):
    """ Defines the GeoJSON output file and its fields. """

    # define CRS
    SRS = osr.SpatialReference()
    SRS.ImportFromEPSG(4326)

    # define driver and output file
    outDriver = ogr.GetDriverByName('GeoJSON')
    outDataSource = outDriver.CreateDataSource(
        os.path.join(path, filename))

    # define layer
    layerName = filename
    outLayer = outDataSource.CreateLayer(
        layerName, SRS, ogr.wkbGeometryCollection)

    for key in fdata:

        # define fieldname and its type
        try:
            float(fdata[key])
            new_field = ogr.FieldDefn(str(key), ogr.OFTReal)

        except ValueError:
            new_field = ogr.FieldDefn(str(key), ogr.OFTString)
            new_field.SetWidth(254)

        # create field
        outLayer.CreateField(new_field)

    return outDataSource


def write_feature(datasource, fdata, fgeom):
    """ Write the feature to the output file. """

    # define layer
    outLayer = datasource.GetLayer(0)
    outFeature = ogr.Feature(outLayer.GetLayerDefn())

    for key in fdata:

        # add data to their respective fields
        try:
            float(fdata[key])
            outFeature.SetField(str(key), float(fdata[key]))

        except ValueError:
            outFeature.SetField(str(key), str(fdata[key]))

    # add geometry
    geom = ogr.CreateGeometryFromWkt(to_shape(fgeom).wkt)
    outFeature.SetGeometry(geom)

    # create feature
    outLayer.CreateFeature(outFeature)

    outFeature = None
