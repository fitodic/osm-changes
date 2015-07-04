from dbase.connection import session
from dbase.tables import Feature, OSMfile
from general import save_result, current_data
from sqlalchemy import and_
from jellyfish import jaro_winkler, levenshtein_distance


def change_jaro_winkler(**kwargs):
    """ Calculates the average Jaro-Winkler percentage of change for the tag of
    interest. """

    # get current data
    list_current = current_data(**kwargs)
    # get tag of interest
    tag = kwargs['tag_of_interest']

    for current in list_current:

        # only process features with TOI
        if current.all_tags.has_key(tag):

            # get all versions of the feature
            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            jwc = []

            for i, feature in enumerate(features):

                if i != 0:
                    # test tags of two consecutive versions
                    if features[i - 1].all_tags.has_key(tag) and \
                            feature.all_tags.has_key(tag):
                        previous_tag = features[
                            i - 1].all_tags[tag]
                        current_tag = feature.all_tags[tag]

                        jwc.append(jaro_winkler(previous_tag, current_tag))

            # calculate average JW percentage of similarity
            if jwc != []:
                result = sum(jwc) / float(len(jwc))

                # save results to the DB
                save_result(kwargs['job_op_id'], current.osm_id, result)


def change_levenshtein(**kwargs):
    """ Calculates the average Levenshtein distance for the tag of interest. """

    # get current data
    list_current = current_data(**kwargs)
    # get tag of interest
    tag = kwargs['tag_of_interest']

    for current in list_current:

        # only process features with TOI
        if current.all_tags.has_key(tag):

            # get all versions of the feature
            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            ld = []

            for i, feature in enumerate(features):

                if i != 0:
                    # test tags of two consecutive versions
                    if features[i - 1].all_tags.has_key(tag) and \
                            feature.all_tags.has_key(tag):
                        previous_tag = features[
                            i - 1].all_tags[tag]
                        current_tag = feature.all_tags[tag]

                        ld.append(
                            levenshtein_distance(previous_tag, current_tag))

            # calculate average Levenshtein distance
            if ld != []:
                result = sum(ld) / float(len(ld))

                # save results to the DB
                save_result(kwargs['job_op_id'], current.osm_id, result)
