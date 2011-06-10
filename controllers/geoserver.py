from urllib import urlencode
from urllib2 import urlopen, Request

def ows():
    lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    content_type = request.vars.get ('Content-Type') or 'text'
    #if request.vars.has_key ('SLD_NAME'):
    #    req_body = {'sld_body': str (db (db.tmp_styles.id == require_int (request.vars.get ('SLD_NAME'))).select ().first ().style_data)}
    #    req_body.update (request.get_vars)
    #    req = Request (data.src + '/ows', urlencode (req_body))
    #else:
    req_body = request.body.read ()
    req = Request (data.src + '/wfs?' + urlencode (request.get_vars), req_body, {
            'Content-Type': content_type,
            })
    map_data = urlopen (req)
    #response.headers['Content-Type'] = 'application/xml'
    return map_data.read () 

def wms():
    return ows ()
    '''lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    map_data = urlopen (data.src + '/wms?' + urlencode (request.get_vars), request.body.read ())
    return map_data.read ()'''

def wfs():
    return ows ()
    '''lookup_id = require_int (request.vars.get ('id'))
    data = dm.get ('maps', lookup_id)
    req = Request (data.src + '/wfs?' + urlencode (request.get_vars), request.body.read (), {
            'Content-Type': 'application/xml',
            })
    map_data = urlopen (req)
    #response.headers['Content-Type'] = 'application/xml'
    return map_data.read () '''

def filter():
    lookup_id = require_int (request.vars.get ('ID'))
    filter_field = require_alphanumeric (request.vars.get ('FIELD'))
    filter_mode = require_alphanumeric (request.vars.get ('MODE'))
    filter_value = require_decimal (request.vars.get ('VALUE'))
    data = dm.get ('maps', lookup_id)
    content_type = request.vars.get ('Content-Type') or 'text'
    post_vars = {}
    post_vars.update (request.vars);
    style = open ('applications/' + request.application + '/templates/geoserver/filter.xsd').read () % {
        'layer_name': data.prefix + ':' + data.filename,
        'field_name': filter_field,
        'filter_value': filter_value,
        }
    post_vars.update ({'sld_body': style})
    
    map_data = urlopen  (data.src + '/wfs', urlencode (post_vars))
    return map_data.read () 

def choropleth():
    from savage.graphics.color import ColorMap, color_to_css
    lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    filter_field = require_alphanumeric (request.vars.get ('FIELD'))
    low_color = require_color (request.vars.get ('LOW_COLOR'))
    high_color = require_color (request.vars.get ('HIGH_COLOR'))
    style = gen_choropleth (data, filter_field, low_color, high_color);
    req_body = {'sld_body': style}
    req_body.update (request.get_vars)
    req = Request (data.src + '/wms', urlencode (req_body))
    response.headers['Content-Type'] = 'image/png'
    return urlopen (req).read ();

    #return json.dumps ({'id': db.tmp_styles.insert (style_data = style)})
    '''post_vars = {}
    post_vars.update (request.vars);
    post_vars.update ({'sld_body': style})
    map_data = urlopen  (data.src + '/wfs', urlencode (post_vars))
    response.headers['Content-Type'] = 'image/png'
    return map_data.read () '''

def xsd():
    response.view = 'geoserver/' + request.args[0] + '.xsd'
    data = json.loads (request.body.read ())
    return {'data': data}
