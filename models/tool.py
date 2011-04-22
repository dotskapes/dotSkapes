import gluon.contrib.simplejson as json

from re import match, findall, match

from tempfile import NamedTemporaryFile
import subprocess
from os import getcwd
#from sys import stdin
#from os import pipe, write, fork, close, waitpid, dup2, execvp

# The tools available
db.define_table ('tool_list',
                 Field ('name', 'string', required = True),
                 Field ('filename', 'string', default = None),
                 Field ('pytool', 'boolean', default = True),
                 Field ('description', 'string'),
                 Field ('user_id', 'integer', default = None),
                 Field ('public', 'boolean', default = False),
)

# All the results run tools
db.define_table ('tool_results',
                 Field ('user_id', 'integer', default = None),
                 Field ('file_id', 'string', required = True),
                 Field ('toolid', 'string', required = True),
                 Field ('type', 'string', required = True),
                 Field ('saved', 'boolean', default = False),
                 Field ('filename', 'string'),
                 Field ('public', 'boolean', default = False),
)

# The analyses that are persistant
db.define_table ('saved_analyses',
                 Field ('user_id', 'integer', default = None),
                 Field ('tool', 'string', required = True), 
                 Field ('filename', 'string', required = True),
                 Field ('json', 'string', required = True),
)

def get_module (filename):
    name = 'applications.' + request.application + '.tool.' + filename
    m = __import__ (name, globals (), locals (), ['ctool'], 0)
    reload (m)
    return m

def get_code (filename):
    file = open ('applications/' + request.application + '/tool/' + filename + '.r')
    return file.read ()

def get_tool(id):
    row = db (db.tool_list.id == id).select ()[0]
    if row.pytool:
        name = 'applications.' + request.application + '.tool.' + row.filename
        mod = __import__ (name, globals (), locals (), ['cargs'], 0)
        reload (mod)
        return dict (python = True, args = mod.cargs, filename = row.filename, id = id)
    else:
        vars = findall ('HS_RequestParam\s*\(([^\)]+)\)', get_code (row.filename))
        params = []
        for string in vars:
            t = []
            while len (string) > 0:
                g = match ('\s*(\'|\")', string)
                if not g:
                    break
                else:
                    q= g.group (1)
                g = match ('\s*' + q + '((([^' + q + ']|(?<=\\\)' + q  + ')*)(?<!\\\)' + q +'\s*,?)', string)       

                #g = match ('\s*([\'\"])((([^\'\"]|(?<=\\\)[\'\"])*)(?<!\\\)[\'\"]\s*,?)', string)
                if g:
                    p = g.group (2)
                    string = string [g.end (1):]
                    t.append (p)
                else:
                    raise HTTP (400, 'Syntax Error')
            params.append (t)
        return dict (python = False, filename = row.filename, args = params, id = id)

def recursiveJSON (ob):
    if type (ob) == str or type (ob) == unicode:
        try:
            ob = json.loads (ob)
        except:
            ob = str (ob)

    if type (ob) == dict:
        d = {}
        for key, value in ob.iteritems ():
            val = recursiveJSON (value)
            d[key] = val
        return d
    elif type (ob) == list:
        l = []
        for item in ob:
            l.append (recursiveJSON (item))
        return l
    else:
        return ob

def clean_filename (filename):
    filename = str (filename)
    if not match ('^[\w\d ]+$', filename):
        return False
    else:
        return True

def load_results (userid = None):
    rows = db ((db.tool_results.saved == True) & (db.tool_results.user_id == userid)).select ()
    result = []
    for r in rows:
        result.append ({'lookup_id': r.id, 'filename': r.filename, 'public': r.public,})
    return json.dumps (result)

def load_analyses (userid = None):
    result = []
    for r in db (db.saved_analyses.user_id == userid).select ():
        result.append ({'tool': r.tool, 'filename': r.filename, 'data': r.json})
    return result

def load_tools (userid = None):
    tmp_pop_tools ()
    rows = db (db.tool_list.public == True).select (db.tool_list.ALL)
    result = []
    for r in rows:
        result.append ({'id': r.id, 'name': r.name, 'desc': r.description})
    return json.dumps (result)

def load_dev_tools (userid=None):
    rows = db ((db.tool_list.public == False) & (db.tool_list.user_id == auth.user.id)).select (db.tool_list.ALL)
    result = []
    for r in rows:
        result.append ({'id': r.id, 'name': r.name, 'desc': r.description})
    return json.dumps (result)
    

def call_py (m):
    connection = deployment_settings.postgis.connection ()
    file_id = str (uuid4 ().int)
    mod = get_module (m['filename'])
    attr = {}
    attr['file'] = open ('applications/' + request.application + '/tool/results/' + file_id, 'w')
    for t in m['args']:
        key = t[0]
        label = t[1]
        tType = t[2]
        val = request.vars.get (key)
        if tType == 'poly_map':
            mapname = json.loads (val)['filename']
            removePrefix = match ('^\w+\:(\w+)$', mapname)
            if not removePrefix:
                raise HTTP (400)
            mapname = removePrefix.group (1)
            attr[key] = loadMap (mapname, enum.POLYGON, enum.POSTGRES, connection=connection)
        elif tType == 'point_map':
            mapname = json.loads (val)['filename']
            removePrefix = match ('^\w+\:(\w+)$', mapname)
            if not removePrefix:
                raise HTTP (400)
            mapname = removePrefix.group (1)
            attr[key] = loadMap (mapname, enum.POINT, enum.POSTGRES, connection=connection)
        elif tType == 'agg':
            attr[key] = recursiveJSON (val)
        elif tType == 'text':
            if len (val) > 0:
                attr[key] = val
            else:
                attr[key] = None
        else:
            attr[key] = val
    r_type = mod.ctool (**attr)
    attr['file'].close ()
    if auth.user:
        user_id = auth.user.id
    else:
        user_id = None
    lookup_id = db.tool_results.insert (file_id = file_id, type = r_type, toolid = m['id'], user_id = user_id)
    return json.dumps ({'id': lookup_id, 'type': r_type})

def call_r (m):
    #from rpy2 import robjects
    #r = robjects.r

    result_id = str (uuid4 ().int)
    result_path = 'applications/' + request.application + '/tool/results/' + result_id

    code = get_code (m['filename'])
    #r ("library ('sp')")
    #r ("library ('rgdal')")
    #r("svg (filename = '" + getcwd () + '/' + result_path  + "')\n")

    setup = "library ('sp')\n"
    setup += "library ('rgdal')\n"
    setup += "svg (filename = '" + getcwd () + '/' + result_path  + "')\n"

    func = 'HS_RequestParam = function (key, name, type, ...) {\n'
    for i, t in enumerate (m['args']):
        key = t[0]
        label = t[1]
        tType = t[2]
        val = request.vars.get (key)
        if i > 0:
            func += 'else '
        if tType == 'poly_map' or tType == 'point_map':
            mapname = json.loads (val)['filename']
            removePrefix = match ('^\w+\:(\w+)$', mapname)
            if not removePrefix:
                raise HTTP (400, "Bad")
            mapname = removePrefix.group (1)
            func += "if (key == '" + key  + "') readOGR (dsn = 'PG:" + postgresString () + "', layer = '" + str (mapname)  + "')\n"
        elif tType == 'text' or  tType == 'attr':
            func += "if (key == '" + key  + "')\n  '" + val + "'\n"
        elif tType == 'number':
            func += "if (key == '" + key  + "')\n  " + str (float (val)) + "\n"
            
    func += "}\n"
    #r (func)

    #for line in code.split ('\n'):
    #    r (line)

    #r ('dev.off ()')

    proc = subprocess.Popen (['R', '--no-save', '--silent'], stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.communicate (setup + func + code + '\ndev.off ()\n')
    if proc.returncode != 0:
        return json.dumps ({'err': str(out[0])})
    #proc.communicate (func)
    #proc.communicate ('dev.off ()')
    #proc.communicate ('\x04')

    lookup_id = db.tool_results.insert (file_id = result_id, type = 'image/svg+xml', toolid = m['id'], user_id = auth.user.id)
    return json.dumps ({'id': lookup_id, 'type': 'image/svg+xml'})


    """file.write ("library ('sp', lib.loc = c ('/home/zack/R-2.12.1/library'))\n")
    file.write ("library ('rgdal', lib.loc = c ('/home/zack/R-2.12.1/library'))\n")
    file.write ("library (sp)\n")
    file.write ("svg (filename = '" + getcwd () + '/' + result_path  + "')\n")
    file.write ("HS_RequestParam = function (key, name, type, ...) {\n")

    for i, t in enumerate (m['args']):
        key = t[0]
        label = t[1]
        tType = t[2]
        val = request.vars.get (key)
        if i > 0:
            file.write ('else ')
        if tType == 'poly_map' or tType == 'point_map':
            mapname = json.loads (val)['id']
            if not match ('^\w*$', mapname):
                raise HTTP (400)
            file.write ("if (key == '" + key  + "') readOGR (dsn = 'PG:" + postgresString () + "', layer = '" + str (mapname)  + "')\n")
        elif tType == 'text':
            file.write ("if (key == '" + key  + "')\n  '" + val + "'\n")
            
    file.write ("}\n")
    
    file.write (code)
    file.write ("q ()\n")

    file.close ()
    
    result = subprocess.check_call (['R-2.12.1', '--no-save', '--silent', '--file='+file_path])
    lookup_id = db.tool_results.insert (file_id = result_id, type = 'image/svg+xml', toolid = m['id'])
    return json.dumps ({'id': lookup_id, 'type': 'image/svg+xml', 'wait': result})"""

def tool_path ():
    return getcwd () + '/applications/' + request.application + '/tool/'

def tool_ext (pytool):
    if pytool:
        ext = '.py'
    else:
        ext = '.r'
    return ext
    
def tmp_pop_tools ():
    pass
    #code = '''pointMap = HS_RequestParam ("key1", "Point Map", "point_map")\n
    #                               polyMap = HS_RequestParam ("key2", "\\\"Poly Map\\\'s\\\"", "poly_map")\n
    #db.tool_list.truncate ()
    #db.tool_list.insert (name = 'Aggregate', filename = 'aggregate', description = 'Aggregate points in a polygon', public = True)
    #db.tool_list.insert (name = 'R Tool', description = 'Run R, test R\'s functionality', pytool = False, filename = "test_r", public = True)
