import gluon.contrib.simplejson as json

from re import match, findall, sub

from tempfile import NamedTemporaryFile
import subprocess
from os import getcwd

tool_model = DM_TableModel (
    DM_Field ('name', 'string', required = True, title = True, text = 'Name'), 
    DM_Field ('filename', 'string', default = None, protected = True),
    DM_Field ('type', 'string', default = 'Python', visible = True), 
    DM_Field ('description', 'string'),
    name = 'Tools',
)

dm.define_datatype ('tools', tool_model)
dm.dup ('tools', 'dev_tools')

dm.define_datatype ('results', DM_TableModel (
        DM_Field ('filename', 'string', required = True, protected = True),
        DM_Field ('type', 'string', required = True, text = 'Type'),
        DM_Field ('name', 'string', title = True, text = 'Name'),
        name = 'Results')
)

dm.define_datatype ('analyses', DM_TableModel (
                 DM_Field ('name', 'string', required = True, title = True),
                 DM_Field ('tool', 'string', required = True), 
                 DM_Field ('json', 'string', required = True),
                 name = 'Analyses')
)
        
# Util Functions

def tool_path ():
    return getcwd () + '/applications/' + request.application + '/tool/'

def tool_ext (pytool):
    if pytool:
        ext = '.py'
    else:
        ext = '.r'
    return ext

def tool_type (tool_data):
    if tool_data['pytool']:
        return 'Python'
    else:
        return 'R'

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

# Read Tool Functions

def get_module (filename):
    filename = sub ('.py', '', filename)
    name = 'applications.' + request.application + '.tool.' + filename
    m = __import__ (name, globals (), locals (), ['ctool'], 0)
    reload (m)
    return m

def get_code (filename):
    file = open ('applications/' + request.application + '/tool/' + filename + '.r')
    return file.read ()

def get_tool(id):
    row = dm.get ('tools', id)
    #row = db (db.tool_list.id == id).select ()[0]
    #row = dm.get ('tools', id)
    if row.type.lower () == 'python':
        mod = get_module (row.filename)
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

# Run Tool Function

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
            #removePrefix = match ('^\w+\:(\w+)$', mapname)
            #if not removePrefix:
            #    raise HTTP (400)
            #mapname = removePrefix.group (1)
            attr[key] = loadMap (mapname, enum.POLYGON, enum.POSTGRES, connection=connection)
        elif tType == 'point_map':
            mapname = json.loads (val)['filename']
            #removePrefix = match ('^\w+\:(\w+)$', mapname)
            #if not removePrefix:
            #    raise HTTP (400)
            #mapname = removePrefix.group (1)
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
    try:
        r_type = mod.ctool (**attr)
    except Exception as ex:
        return {'err': str (ex)}
    attr['file'].close ()
    if auth.user:
        user_id = auth.user.id
    else:
        user_id = None
    lookup_id = dm.insert ('results', filename = file_id, type = r_type)
    return dm.get ('results', lookup_id)

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
        return {'err': str(out[0])}
    #proc.communicate (func)
    #proc.communicate ('dev.off ()')
    #proc.communicate ('\x04')

    lookup_id = dm.insert ('results', filename = result_id, type = 'image/svg+xml')
    return dm.get ('results', lookup_id)

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

# Dev Functions

def dev_create_tool (name, desc, tool_type):
    pytool = (tool_type.lower () == 'python')
    filename = uuid4 ().hex + tool_ext (pytool)
    path = tool_path () + filename
    file = open (path, 'w')
    if pytool:
        file.write ('''# Add parameters here. Each parameter is of the form (param_name, param_title, param_type)\ncargs = []\n\n# Implement tool function here. Parameters are accessible as attr[param_name].\n# The return type should be the MIME type of the result.\n# An IO Stream attr[\'file\'] is provided to store the result.\ndef ctool (**attr):\n    pass''')
    else:
        file.write ('''# Add R code here. use the function HS_RequestParam (key, name, type)\n# Use this function to insert parameters from the main applciation to your tool\n''')
    file.close ()
    kwargs = dict (name = name, type = tool_type, description = desc, filename = filename)
    id = dm.insert ('dev_tools', **kwargs)
    dm.link ('dev_tools', id)
    return dm.get ('dev_tools', id)

def dev_read_code (filename):
    file = open (tool_path () + filename, 'r')
    buffer = file.read ()
    file.close ()
    return buffer

def dev_format_code (buf):
    buffer = buf
    buffer = buffer.replace (',', ',&#8203;')
    buffer = buffer.replace (' ', '&nbsp;')
    buffer = buffer.replace ('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    buffer = buffer.replace ('\n', '<br />\n')
    return buffer

def dev_save_code (filename, buffer):
    file = open (tool_path () + filename, 'w')
    file.write (buffer)
    file.close ()


# Analysis Functions

def format_analysis (vars, tool_id):
    mod = get_tool (tool_id)
    pairs = []
    for ob in mod['args']:
        key = ob[0]
        pairs.append ((key, request.vars.get (key)))
    return json.dumps (dict (pairs))
