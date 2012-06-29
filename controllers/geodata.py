import simplejson as json
from re import match
from urllib import urlencode
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

def read():
    lookup_id = require_alphanumeric (request.vars.get ('id'))
    data = dm.get ('maps', lookup_id)
    start = require_int (request.vars.get ('start'))
    limit = require_int (request.vars.get ('limit'))
    return json.dumps (load_map_attributes (data, start, limit))
    '''map_data = urlopen (data.src + '/ows', urlencode ({
                'service': 'wfs',
                'version': '1.1.0',
                'request': 'GetFeature',
                'typename': data.prefix + ':' + data.filename,
                'outputformat': 'json',
                })
             )
    #return map_data.read ()
    entry_list = []
    for ob in json.loads (map_data.read ())['features']:
        result = {'id': ob['id']}
        result.update (ob['properties'])
        #result.update ({'geom': ob['geometry']['coordinates'], 'id': ob['id']})
        entry_list.append (result)
    return json.dumps ({'features': entry_list})'''

def columns():
    lookup_id = require_alphanumeric (request.vars.get ('id'))
    data = dm.get ('maps', lookup_id)
    return json.dumps ({'id': lookup_id, 'columns': load_fields (data)})

def maps():
    file = urlopen (deployment_settings.geoserver.wms_capabilities ())
    buffer = file.read ()
    soup = BeautifulStoneSoup (buffer)
    layers = soup.findAll (name = 'layer')
    results = []
    for l in layers:
        name = l.find ('title')
        id = l.find ('name')
        if name and id:
            text = name.string
            if not text:
                text = id.string
            m = match ('^([^\:]+)\:(.+)$', id.string)
            if m:
                p = m.group (1)
                f = m.group (2)
            else:
                p = '',
                f = id.string
            results.append ({'prefix': p, 'filename': f, 'name': text, 'type': 'db'})
    return json.dumps (results)

def kw():
    from BeautifulSoup import BeautifulStoneSoup 
    from urllib2 import urlopen

    tmp_create_lit ()
    disease = request.vars.get ('d')
    result = db.executesql ('''
    SELECT keyword.kw, counts.count 
    FROM (SELECT keycount.kw_id, keycount.count 
          FROM (SELECT id 
                FROM disease 
                WHERE d = '%s') AS diseases
          INNER JOIN keycount
          ON keycount.d_id = diseases.id) AS counts
    INNER JOIN keyword
    ON keyword.id = counts.kw_id;
    ''' % (disease,))
    rList = []
    capabilities = urlopen (deployment_settings.geoserver.wms_capabilities ()).read ()
    soup = BeautifulStoneSoup (capabilities)
    keywords = soup.findAll (name = 'keyword')
    for r in result:
        words = []
        for k in keywords:
            if k.string == r[0]:
                words.append (k)
        mapList = []
        for w in words:
            layer = w.parent.parent
            id = layer.find ('name').string
            name = layer.find ('title').string
            mapList.append ({'filename': id, 'name': name, 'type': 'db'})
        d = dict (kw = r[0], count = r[1], numMaps = len (words), maps = mapList)
        rList.append (d)
    return json.dumps (rList)

def reset_maps():
    if not auth.user:
        raise HTTP (400)
    db (db.saved_maps.user_id == auth.user.id).update (json = '{}')
    return 'Ok'
    
def save_maps():
    if not auth.user:
        raise HTTP (400)
    mapList = request.vars.get ('data')
    if mapList is None:
        raise HTTP (400)
    db (db.saved_maps.user_id == auth.user.id).update (json = mapList)

'''def save_slice():
    if not auth.user:
        raise HTTP (400)
    filename = request.vars.get ('filename')
    name = request.vars.get ('name')
    subset = request.vars.get ('subset')'''

def describe_tmp():
    lookup_id = request.vars.get ('id')
    data = dm.get ('maps', lookup_id)
    return urlopen (data.src + '?service=WFS&request=DescribeFeatureType&typename=' + data.prefix + ':' + data.filename + '&version=1.1.0').read ()

def export():
    import base64
    raw_data = request.body.read ()
    data = raw_data[raw_data.index (','):]
    response.headers['Content-type'] ='image/png'
    #response.headers['Content-Disposition'] = 'attachment; filename="webgl_map.png"'
    return base64.decodestring (data)
