from urllib import urlencode
from urllib2 import urlopen

map_model = DM_TableModel (DM_Field ('name', 'string', required = True, title = True, text = 'Name'),
                           DM_Field ('prefix', 'string', default = '', visible = False),
                           DM_Field ('filename', 'string', required = True, visible = False),
                           DM_Field ('src', 'string', required = True, visible = True),
                           DM_Field ('styles', 'string', default = '', visible = False),
                           name = 'Maps',
)

dm.define_datatype ('maps', map_model)

# Deprecated use geoserver.load_map instead
def geodata_json (lookup_id):
    data = dm.get ('maps', lookup_id)
    map_data = urlopen (data.src + '/wfs', urlencode ({
                'service': 'wfs',
                'version': '1.1.0',
                'request': 'GetFeature',
                'typename': data.prefix + ':' + data.filename,
                'outputformat': 'JSON',
                })
            )
    return map_data.read ()
    
