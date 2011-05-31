class Key:
    def __init__ (self, data):
        self.data = data

    def __str__ (self):
        return str (self.data)

SHP = Key ('SHP')
POSTGRES = Key ('POSTGRES')
GEOSERVER = Key ('GEOSERVER')

POLYGON = Key ('POLYGON')
POINT = Key ('POINT')

ONE_TO_ONE = Key ('ONE_TO_ONE')
MANY_TO_ONE = Key ('MANY_TO_ONE')
