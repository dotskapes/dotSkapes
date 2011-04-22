from re import findall
import psycopg2
from . import Polygon, Point, Map
import enum

def loadMap (mapName, geomType, mapType, connection = None):
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
