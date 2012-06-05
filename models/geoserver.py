from urllib import urlencode
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

db.define_table ('geoserver_sources', 
                 Field ('loc', 'string', required = True))

def sync_geoserver (path):
    file = urlopen (path + '?SERVICE=WFS&REQUEST=GetCapabilities')
    buffer = file.read ()
    soup = BeautifulStoneSoup (buffer)
    layers = soup.findAll (name = 'featuretype')
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
            if dm.query ('maps', prefix = p, filename = f, name = text, src = path).first ():
                pass
            else:
                id = dm.insert ('maps', prefix = p, filename = f, name = text, src = path, public = True)
                keywords = l.findAll (name = 'keyword')
                kw = []
                for k in keywords:
                    kw.append (k.string)
                #dm.keywords ('maps', id, kw)

def load_fields (data):
    map_data = urlopen (data.src + '/ows', urlencode ({
                'service': 'wfs',
                'version': '1.1.0',
                'request': 'DescribeFeatureType',
                'typename': data.prefix + ':' + data.filename,
                #'outputformat': 'json',
                })
             )
    doc = BeautifulStoneSoup (map_data.read ())
    elements = doc.find ('xsd:complextype')
    tags = elements.findAll ('xsd:element')
    names = []
    for t in tags:
        if match ('^gml:', t['type']):
            continue
        names.append (str (t['name']))
    return names

def load_map (data):
    map_data = urlopen (data.src + '?', urlencode ({
                'service': 'wfs',
                'version': '1.1.0',
                'request': 'GetFeature',
                'typename': data.prefix + ':' + data.filename,
                'outputformat': 'JSON',
                })
            )
    return map_data.read ()

def load_map_attributes (data, start = None, limit = None):
    if not session.has_key ('current_map') or not session['current_map'][0] == data.id:
        map_data = urlopen (data.src + '/ows', urlencode ({
                    'service': 'wfs',
                    'version': '1.1.0',
                    'request': 'GetFeature',
                    'typename': data.prefix + ':' + data.filename,
                    'outputformat': 'json',
                    })
                )
        map_attr = []
        for ob in json.loads (map_data.read ())['features']:
            result = {'id': ob['id']}
            result.update (ob['properties'])
            map_attr.append (result)
        #session['current_map'] = (data.id, map_attr)
    else:
        map_attr = session['current_map'][1]
    if not limit:
        return {'features': map_attr}
    else:
        return {'features': map_attr[start:start + limit]}

def gen_choropleth (map_index, sort_field, low_color, high_color):
    from savage.graphics.color import ColorMap, color_to_css
    key = map_index.src + map_index.filename + sort_field + color_to_css (low_color) + color_to_css (high_color)
    def create_choro ():
        attr = load_map_attributes (map_index)
        data_list = []
        for item in attr['features']:
            data_list.append ((item['id'], item[sort_field]))
            data_list.sort (key = lambda x: x[0])
            cm = ColorMap (low_color, high_color, len (data_list))
        choro = json.dumps ({'layer': map_index.prefix + ':' + map_index.filename, 'filter': zip (map (lambda x: x[0], data_list), map (color_to_css, cm))})
        return urlopen ('http://127.0.0.1:' + str (deployment_settings.web2py.port) + '/' + request.application + '/geoserver/xsd/choropleth', choro).read ()
    return cache.ram (key, create_choro, time_expire = 20);
    
