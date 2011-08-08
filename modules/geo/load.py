from re import findall
import psycopg2
from . import Polygon, Point, Map
import enum
import simplejson as json

from urllib import urlencode
from urllib2 import urlopen

def loadMap (mapName, geomType, mapType, connection = None, location = None):
    if mapType == enum.SHP:
        raise NotImplementedError ()
    elif mapType == enum.POSTGRES:
        sqlString = """SELECT column_name, udt_name FROM information_schema.columns WHERE table_name = '%s';""" % mapName
        cursor = connection.cursor ()
        cursor.execute (sqlString)
        geometry = ''
        mapping = []
        fields = []
        for entry in cursor:
            key, value = entry
            mapping.append (key)
            if value == 'geometry':
                geometry = key
                fields.append ('AsText (' + key  + ')')
            else:
                fields.append (key)

        sqlString = """SELECT %s FROM %s """ % (', '.join (fields), mapName)
        cursor.execute (sqlString)
        shapes = Map (name = mapName)
        for entry in cursor:
            values = dict (zip (mapping, entry))
            geom = textToList (values[geometry])
            del values[geometry]
            if geomType == enum.POLYGON:
                s = Polygon (geom, values)
            elif geomType == enum.POINT:
                s = Point (geom[0][0], values)
            shapes.append (s)
        return shapes
    elif mapType == enum.GEOSERVER:
        map_data = urlopen (location + '/wfs', urlencode ({
                    'service': 'wfs',
                    'version': '1.1.0',
                    'request': 'GetFeature',
                    'typename': mapName,
                    'outputformat': 'JSON',
                    })
               )
        map_ob = json.loads (map_data.read ())
        shapes = Map (name = mapName)
        for feature in map_ob['features']:
            if geomType == enum.POLYGON:
                geomList = []
                for item in feature['geometry']['coordinates']:
                    for ob in item:
                        geomList.append (ob)
                    #s = Polygon (feature['geometry']['coordinates'][0], feature['properties'])
                s = Polygon (geomList, feature['properties'], True)
                shapes.append (s)
            elif geomType == enum.POINT:
                ob = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Point':
                    s = Point (ob, feature['properties'], True)
                    shapes.append (s)
                elif feature['geometry']['type'] == 'MultiPoint':
                    for p in ob:
                        s = Point (p, feature['properties'], True)
                        shapes.append (s)
        return shapes


def loadPolygonPostGIS (mapName, connection):
    sqlString = """SELECT column_name, udt_name FROM information_schema.columns WHERE table_name = '%s';""" % mapName
    cursor = connection.cursor ()
    cursor.execute (sqlString)
    geometry = ''
    mapping = []
    fields = []
    for entry in cursor:
        key, value = entry
        mapping.append (key)
        if value == 'geometry':
            geometry = key
            fields.append ('AsText (' + key  + ')')
        else:
            fields.append (key)

    sqlString = """SELECT %s FROM %s """ % (', '.join (fields), mapName)
    cursor.execute (sqlString)
    polys = SpatialList ()
    for entry in cursor:
        values = dict (zip (mapping, entry))
        geom = textToList (values[geometry])
        del values[geometry]
        polys.append (Polygon (geom, values))

    return polys


def textToList (string):
    stringCoords = findall ('\(([^\(\)]+)\)', string)
    geomCoords = []
    for s in stringCoords:
        values = s.split (',')
        shape = []
        for c in values:
            pair = c.split (' ')
            pair = map (float, pair)
            shape.append (pair)
        geomCoords.append (shape)
    return geomCoords
