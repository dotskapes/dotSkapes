from urllib import urlencode
from urllib2 import urlopen

def wms():
    lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    del request.vars['ID']
    map_data = urlopen (data.src + '/wms', urlencode (request.vars))
    response.headers['Content-Type'] = 'image/png'
    return map_data.read () 

def wfs():
    lookup_id = require_int (request.vars.get ('id'))
    data = dm.get ('maps', lookup_id)
    del request.vars['id']
    map_data = urlopen (data.src + '/wfs', urlencode (request.vars))
    response.headers['Content-Type'] = 'text/xml'
    return map_data.read () 
