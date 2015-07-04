from dbase.connection import session
from dbase.tables import Feature, OSMfile
from general import save_result, current_data, find_geom
from sqlalchemy import and_


def count_inserts(**kwargs):
    """ Counts the number of tag insertions. """

    # get current data
    list_current = current_data(**kwargs)

    for i, current in enumerate(list_current):

        # select all version of the feature
        features = session.query(Feature).filter(
            Feature.osm_id == current.osm_id).order_by(
            Feature.osm_version).all()

        # initialize counter
        total = 0

        if len(features) >= 2:
            for i, feature in enumerate(features):

                if i != 0:
                    previous = features[i - 1]

                    if feature.all_tags != previous.all_tags:
                        # go through all tags
                        for key in feature.all_tags:
                            if not previous.all_tags.has_key(key):
                                total += 1

            # save results to the DB
            save_result(kwargs['job_op_id'], current.osm_id, total)


def count_updates(**kwargs):
    """ Counts the number of modified tags or the number of modifications to a
    certain tag of interest. """

    # get current data
    list_current = current_data(**kwargs)

    # find TOI
    try:
        tag = kwargs['tag_of_interest']
    except KeyError:
        tag = None

    for i, current in enumerate(list_current):

        # select features based on the osm_id
        features = session.query(Feature).filter(
            Feature.osm_id == current.osm_id).order_by(
            Feature.osm_version).all()

        # initialize counter
        total = 0

        if len(features) >= 2:
            for i, feature in enumerate(features):

                if i != 0:
                    previous = features[i - 1]

                    # if no tag was specified
                    if not tag:
                        for key in feature.all_tags:
                            # go through all tags
                            if previous.all_tags.has_key(key) and \
                                    feature.all_tags.has_key(key) and \
                                    previous.all_tags[key] != feature.all_tags[key]:
                                total += 1

                    # if a tag was specified
                    else:
                        # check the specified tag
                        if previous.all_tags.has_key(tag) and \
                                feature.all_tags.has_key(tag) and \
                                previous.all_tags[tag] != feature.all_tags[tag]:
                            total += 1

            # save results to the DB
            save_result(kwargs['job_op_id'], current.osm_id, total)


def count_deletions(**kwargs):
    """ Counts the number of deleted tags. """

    # get current data
    list_current = current_data(**kwargs)

    # check if any specific tag was specified
    try:
        tag = kwargs['tag_of_interest']
    except KeyError:
        tag = None

    for i, current in enumerate(list_current):

        # select features based on the osm_id
        features = session.query(Feature).filter(
            Feature.osm_id == current.osm_id).order_by(
            Feature.osm_version).all()

        # initialize counter
        total = 0

        if len(features) >= 2:

            for i, feature in enumerate(features):

                if i != 0:
                    previous = features[i - 1]

                    # if no tag was specified
                    if tag == None:
                        # go through all tags
                        for key in previous.all_tags:
                            if previous.all_tags.has_key(key) == True and \
                                    feature.all_tags.has_key(key) == False:
                                total += 1

                    # if a tag was specified
                    else:
                        # check the specified tag
                        if previous.all_tags.has_key(tag) == True and \
                                feature.all_tags.has_key(tag) == False:
                            total += 1

            # save results to the DB
            save_result(kwargs['job_op_id'], current.osm_id, total)


def count_geom_changes(**kwargs):
    """ Counts the number of geometric changes. """

    # get current data
    list_current = current_data(**kwargs)

    for i, current in enumerate(list_current):

        if current.osm_version >= kwargs['osm_version']:
            # select features based on the osm_id
            features = session.query(Feature).filter(
                Feature.osm_id == current.osm_id).order_by(
                Feature.osm_version).all()

            # initialize counter
            total = 0

            if len(features) >= 2:
                for i, feature in enumerate(features):

                    if i != 0:
                        previous_geom = find_geom(features[i - 1])
                        current_geom = find_geom(feature)

                        if not previous_geom.almost_equals(current_geom):
                            total += 1

            # save results to the DB
            save_result(kwargs['job_op_id'], current.osm_id, total)
