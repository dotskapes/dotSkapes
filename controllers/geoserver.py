from urllib import urlencode
from urllib2 import urlopen, Request
from re import search

def ows():
    lookup_id = require_int (request.vars.get ('ID'))
    data = dm.get ('maps', lookup_id)
    request.get_vars['layers'] = data.prefix + ':' + data.filename
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

def sources():
    sources = db (db.geoserver_sources.id > 0).select ()
    return json.dumps (map (lambda x: x.loc, sources))

def sync():
    require_role (admin_role)
    path = require_http (request.vars.get ('path'))
    try:
        sync_geoserver (path)
        if not db (db.geoserver_sources.loc == path).select ().first ():
            db.geoserver_sources.insert (loc = path)
            return json.dumps ({'code': 1, 'path': path})
        return json.dumps ({'code': 0})
    except:
        return json.dumps ({'code': -1, 'err': 'An error occurred'})

def desync():
    require_role (admin_role)
    path = require_http (request.vars.get ('path'))
    result = db (db.geoserver_sources.loc == path).select ().first ()
    if not result:
        return json.dumps ({'err': 'Geoserver not found'})
    dm.delete ('maps', src = result.loc)
    db (db.geoserver_sources.id == result.id).delete ()
    return json.dumps ({'code': 0})

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

def upload():
    require_logged_in ()
    form = FORM (INPUT (_type="file", _name="map"), BR (), INPUT (_type="submit", _value="Upload"))
    if form.accepts (request, session):
        from os import mkdir
        from shutil import rmtree
        path = getcwd () + '/applications/' + request.application + '/.tmp/' + uuid4 ().hex
        filename = path + '/' + sub ('/', '', form.vars.map.filename)
        mkdir (path)
        buffer = open (filename, 'w')
        buffer.write (form.vars.map.file.read ())
        buffer.close ()
        proc = subprocess.Popen (['tar', '-xvf', filename, '-C', path], stdout = subprocess.PIPE)
        #proc = subprocess.Popen (['tar', '-tvf', filename], stdout = subprocess.PIPE)
        files = proc.communicate ()[0].split ('\n')
        #files = files [:len (files) - 2]
        matches = map (lambda x: search ('\.shp$', x), files)
        for item, m in zip (files, matches):
            if m:
                table_name = 'upload_' + uuid4 ().hex
                dp = deployment_settings.postgis
                dg = deployment_settings.geoserver
                proc1 = subprocess.Popen (['shp2pgsql', path + '/' + item, table_name], stdout = subprocess.PIPE)
                proc2 = subprocess.call (['psql', '-h', dp.host, '-p', str (dp.port), '-d', dp.database, '-U', dp.username], stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = proc1.stdout)
                proc1.communicate ()
                req_body = '<featureType><name>%s</name><title>%s</title><srs>EPSG:4326</srs></featureType>' % (table_name, sub ('.shp', '', item))
                req = Request ('%s:%d/geoserver/rest/workspaces/%s/datastores/%s/featuretypes' % (dg.host, dg.port, dg.workspace, dg.pgis_store), req_body, {
                        'Content-Type': 'text/xml',
                        })
                urlopen (req)
                rmtree (path)
                return 'Ok'
                #return ' '.join(['curl', '-u', '%s:%s' % (deployment_settings.geoserver.username, deployment_settings.geoserver.password), '-XPUT', '-H', '"Content-type: text/plain"', '-d', 'file://%s' % path, 'http://localhost:%d/geoserver/rest/workspaces/%s/datastores/%s/external.shp' % (deployment_settings.geoserver.port, deployment_settings.geoserver.namespace, uuid4 ().hex)])
                #proc = subprocess.Popen (['curl', '-u', '%s:%s' % (deployment_settings.geoserver.username, deployment_settings.geoserver.password), '-XPUT', '-H', '"Content-type: text/plain"', '-d', 'file://%s' % path, 'http://localhost:%d/geoserver/rest/workspaces/%s/datastores/%s/external.shp' % (deployment_settings.geoserver.port, deployment_settings.geoserver.namespace, uuid4 ().hex)], stdout = subprocess.PIPE)
                #return str (proc.communicate ()[0])
    return form
