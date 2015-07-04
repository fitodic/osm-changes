import logging
LOG = logging.getLogger(__file__)

import osr
import ogr
import os

import shapely.wkb
from shapely.validation import explain_validity


def prepare_osm_id(feature, layer):

    osm_id = None
    osm_way_id = None

    if feature.GetField('osm_id') != None:
        osm_id = feature.GetField('osm_id')
    elif feature.GetField('osm_way_id') != None:
        osm_way_id = feature.GetField('osm_way_id')

    if layer == 'points':
        return 'N{}'.format(osm_id)
    elif layer == 'lines':
        return 'W{}'.format(osm_id)
    elif layer == 'multipolygons':
        if not(osm_id) and osm_way_id:
            return 'W{}'.format(osm_way_id)
        elif osm_id and not(osm_way_id):
            return 'R{}'.format(osm_id)
        else:
            LOG.error('Can\'t detect osm_id, discarding ...')
            return None
    elif layer == 'multilinestrings':
        return 'R{}'.format(osm_id)
    elif layer == 'other_relations':
        return 'R{}'.format(osm_id)
    else:
        LOG.error('Got unsupported layer %s, discarding ...')
        return None


def check_bad_geom(geom, osm_id):
    """
    Check if geom is valid
    """
    try:
        # check if we can parse the geom and determine why is geometry
        # invalid
        tst_geom = shapely.wkb.loads(geom.ExportToWkb())
        if tst_geom.is_valid:
            return False
        else:
            reason = explain_validity(tst_geom)
            LOG.error(
                'Bad geometry for the feature %s, reason: %s', osm_id, reason
            )
    except:
        reason = 'BONKERS!'
        LOG.critical('BONKERS geometry for the feature %s', osm_id)

    return reason
