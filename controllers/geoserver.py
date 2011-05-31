from urllib import urlencode
from urllib2 import urlopen

def wms():
    lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    map_data = urlopen (data.src + '/wms', urlencode (request.vars))
    return map_data.read ()
