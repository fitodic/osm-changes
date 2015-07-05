# osm-changes
---------------------------
##Estimate the quality of OSM features based on their changes

OpenStreetMap (OSM) features experience changes which can span from adding or removing certain tags to updating existing tags or geometries. These changes can increase the overall quality of the OSM dataset, but they can also indicate features affected by significant changes. This Python tool is designed to analyze and determine the quality of OSM features.

The following operations are currently available:
1. *Count tag inserts, deletions, updates and geometric changes*
Detect the locations of certain types of changes.
2. *Evaluate changes using [string matching techniques](https://en.wikipedia.org/wiki/Approximate_string_matching)*
Use the Jaro-Winkler metrics or the Levenshtein distance to analyze the changes in certain types of tags (e.g. name, operator, etc.). The similarity between strings can be indicative of the type of changes, such as correction of typographical errors or changes in ownership.
3. *Determine the currency of spatial objects*
Distinguishes between up-to-date and out-of-date features by calculating the difference between the feature's timestamp and the median timestamp of the analyzed group. Inapplicable to long-standing features (e.g. castles, highways, etc.)
4. *Estimate geometric changes*
Movements of points, increases/reductions of lengths/areas in (Multi)LineStrings/(Multi)Polygons

---------------------------------

###Requirements
1. [PostgreSQL 9.3](http://www.postgresql.org/)
2. [PostGIS 2.1](http://postgis.net/)
3. [Python 2.7](https://www.python.org/download/releases/2.7/)
3. [GDAL/OGR](https://pcjericks.github.io/py-gdalogr-cookbook/)
4. [SQLAlchemy](http://www.sqlalchemy.org/)
5. [GeoAlchemy2](http://geoalchemy-2.readthedocs.org/en/0.2.4/)
6. [Shapely](http://toblerity.org/shapely/)
7. [Jellyfish](https://pypi.python.org/pypi/jellyfish)
8. [ArgParse](https://docs.python.org/2.7/library/argparse.html)

###OSM data extraction 
Input data: [OSM PBF](http://wiki.openstreetmap.org/wiki/Planet.osm) files
Modifications: [Osmconvert](http://wiki.openstreetmap.org/wiki/Osmconvert), [Osmfilter](http://wiki.openstreetmap.org/wiki/Osmfilter)
Usage:
```
$ python osm-changes/extract.py osm-changes/data/INPUTFILE.osm.pbf
```

**Warning**:
The name of the input file should contain its creation date (the rest of the name is optional): **YYYYMMDD-name.osm.pbf**

###OSM data processing
Output format: GeoJSON
Location of the output files (and several examples): ./osm-changes/output
Usage:
```
$ python osm-changes/main.py "job_name" "feature_key" "feature_value" osm_version -ogj -optional_arguments
```
For more info type:
```
$ python osm-changes/main.py -h
```

###Examples
See ./osm-changes/output