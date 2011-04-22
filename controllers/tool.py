import gluon.contrib.simplejson as json
from uuid import uuid4

from geo import enum
from geo.load import loadMap

from re import match

def user():
    return str (auth.user.id)

def args():
    if not auth.user:
        raise HTTP (400)
    name = request.vars.get ('tool')
    if not name:
        raise HTTP (400, 'Need Tool Name')
    mod = get_tool (name)
    return json.dumps (mod['args'])

def call():
    if not auth.user:
        raise HTTP (400)
    name = request.vars.get ('tool')
    if not name:
        raise HTTP (400, 'Need Tool Name')
    m = get_tool (name)
    if m['python']:
        return call_py (m)
    else:
        return call_r (m)

'''def call_r(r_script, **kw_maps):
    p = pipe ()
    pid = fork ()

    if pid:
        close (p[0])
        rfile = open (r_script, 'r')

        write (p[1], "library (rgdal)\n")
        for key, value in kw_maps.iteritems ():
            write (p[1], str (key) + " = readOGR (dsn = 'PG:" + postgresString () + "', layer = '" + str (value)  + "')\n")

        write (p[1], rfile.read () + '\n')
        write (p[1], "q ()\n")
        waitpid (pid, 0)
    else:
        close (p[1])
        dup2 (p[0], stdin.fileno ())
        execvp ('R-2.12.1', ['R-2.12.1', '--no-save', '--quiet'])
        exit (1)'''

def get_result():
    lookup_id = int (request.vars.get ('id'))
    results = db (db.tool_results.id == lookup_id).select ()
    if len (results) == 0:
        raise HTTP (400, "Could not open analysis result")
    result = results[0]
    if not result.public:
        if not auth.user:
            raise HTTP (400, 'Permission Denied')
        if result.user_id != auth.user.id:
            raise HTTP (400, 'Permission Denied')
    file = open ('applications/' + request.application + '/tool/results/' + result.file_id, 'r')
    response.headers['Content-Type'] = result.type
    return file.read ()

def result_perm():
    if not auth.user:
        raise HTTP (400, 'Permission Denied')
    lookup_id = int (request.vars.get ('id'))
    perm = bool (int (request.vars.get ('perm')))
    results = db (db.tool_results.id == lookup_id).select ()
    if len (results) == 0:
        raise HTTP (400, "Could not locate analysis result")
    result = results[0]
    if result.user_id != auth.user.id:
        raise HTTP (400, 'Permission Denied')
    db (db.tool_results.id == lookup_id).update (public = perm)
    return str (db (db.tool_results.id == lookup_id).select ()[0].public)

def result_type():
    if not auth.user:
        raise HTTP (400)
    lookup_id = int (request.vars.get ('id'))
    result = db (db.tool_results.id == lookup_id).select ()[0]
    return result.type

def save_result():
    if not auth.user:
        raise HTTP (400)
    if not auth.user:
        raise HTTP (400, "Please authenticate")
    lookup_id = int (request.vars.get ('id'))
    filename = str (request.vars.get ('filename'))
    if not clean_filename (filename):
        return json.dumps ({'err': 'Bad filename'})
    #id = db.tool_saved.insert (filename = filename, file_id = lookup_id)
    db (db.tool_results.id == lookup_id).update (saved = True, filename = filename)
    return json.dumps ({'id': lookup_id})
    
"""def load_result():
    #rows = db ().select (db.tool_saved.ALL)
    rows = db (db.tool_results.saved == True).select ()
    result = []
    for r in rows:
        result.append ({'id': r.id, 'filename': r.filename})
    return json.dumps (result)"""
        
def save_analysis():
    if not auth.user:
        raise HTTP (400)
    tool_ob = json.loads (request.vars.get ('tool'))
    filename = request.vars.get ('filename')
    if not clean_filename (filename):
        return json.dumps ({'err': 'Bad filename'})
    mod = get_tool (tool_ob['id'])
    pairs = []
    for ob in mod['args']:
        key = ob[0]
        pairs.append ((key, request.vars.get (key)))
    val = json.dumps (dict (pairs))
    lookup_id = db.saved_analyses.insert (tool = request.vars.get ('tool'), filename = filename, json = val, user_id = auth.user.id)
    return json.dumps ({'id': lookup_id})

'''def create():
    if not auth.user:
        raise HTTP (400)
    name = request.vars.get ('title')
    pytool = (request.vars.get ('type') == 'python')
    description = request.vars.get ('desc')
    if pytool:
        ext = '.py'
    else:
        ext = '.r'
    file = open ('applications/' + request.application + '/tool/' +  name + ext, 'w')
    code = request.vars.get ('text')
    file.write (code)
    file.close ()
    db.tool_list.insert (name = name, pytool = pytool, description = description, filename = name)
'''
def create():
    if not auth.user:
        raise HTTP (400, "Permission Denied")
    name = request.vars.get ('name')
    #description = request.vars.get ('desc')
    description = "None"
    pytool = (request.vars.get ('type') == 'python')
    if pytool:
        ext = '.py'
    else:
        ext = '.r'
    path = 'applications/' + request.application + '/tool/' +  name
    try:
        file = open (path + '.py')
        return json.dumps ({'err': 'Cannot create file'})
    except:
        pass
    try:
        file = open (path + '.r')
        return json.dumps ({'err': 'Cannot create file'})
    except:
        pass

    file = open (path + ext, 'w')

    if pytool:
        file.write ('''# Add parameters here. Each parameter is of the form (param_name, param_title, param_type)\ncargs = []\n\n# Implement tool function here. Parameters are accessible as attr[param_name].\n# The return type should be the MIME type of the result.\n# An IO Stream attr[\'file\'] is provided to store the result.\ndef ctool (**attr):\n    pass''')
    else:
        file.write ('''# Add R code here. use the function HS_RequestParam (key, name, type)\n# Use this function to insert parameters from the main applciation to your tool\n''')
    
    file.close ()
    id = db.tool_list.insert (name = name, pytool = pytool, description = description, filename = name, user_id = auth.user.id)    
    return json.dumps ({'id': id, 'name': name, 'type': pytool})

def read():
    lookup_id = int (request.vars.get ('id'))
    result = db (db.tool_list.id == lookup_id).select ()[0]
    if not result.public:
        if not auth.user:
            raise HTTP (400)
        if auth.user.id != result.user_id:
            raise HTTP (400)
    file = open (tool_path () + result.filename + tool_ext (result.pytool), 'r')
    buffer = file.read ()
    file.close ()
    buffer = buffer.replace (',', ',&#8203;')
    buffer = buffer.replace (' ', '&nbsp;')
    buffer = buffer.replace ('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    buffer = buffer.replace ('\n', '<br />\n')
    return buffer    

def dev_code():
    if not auth.user:
        raise HTTP (400)
    if not auth.has_membership ('Developer', auth.user.id):
        raise HTTP (400)
    lookup_id = int (request.vars.get ('id'))
    result = db (db.tool_list.id == lookup_id).select ()[0]
    if not result.public:
        if auth.user.id != result.user_id:
            raise HTTP (400)
    file = open (tool_path () + result.filename + tool_ext (result.pytool), 'r')
    buffer = file.read ()
    file.close ()
    return buffer

def dev_save():
    if not auth.user:
        raise HTTP (400)
    if not auth.has_membership ('Developer', auth.user.id):
        raise HTTP (400)
    lookup_id = int (request.vars.get ('id'))
    text = request.vars.get ('text')
    result = db (db.tool_list.id == lookup_id).select ()[0]
    if auth.user.id != result.user_id:
        raise HTTP (400)
    file = open (tool_path () + result.filename + tool_ext (result.pytool), 'w')
    file.write (text)
    file.close ()

def dev_delete():
    if not auth.user:
        raise HTTP (400)
    if not auth.has_membership ('Developer', auth.user.id):
        raise HTTP (400)
    lookup_id = int (request.vars.get ('id'))
    db (db.tool_list.id == lookup_id).delete ()

def publish():
    lookup_id = int (request.vars.get ('id'))
    db (db.tool_list.id == lookup_id).update (public = True);

