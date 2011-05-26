import gluon.contrib.simplejson as json
from uuid import uuid4

from geo import enum
from geo.load import loadMap

from re import match, sub


def dev():
    require_role (dev_role)
    if request.args[0] == 'create':
        name = require_text (request.vars.get ('name'))
        desc = require_text (request.vars.get ('desc'))
        tool_type = require_alphanumeric (request.vars.get ('type'))
        return dev_create_tool (name, desc, tool_type).json ()
    elif request.args[0] == 'code':
        lookup_id = require_int (request.vars.get ('id'))
        tool_data = dm.get ('dev_tools', lookup_id)
        buffer = dev_read_code (tool_data.filename)
        return buffer
    elif request.args[0] == 'save':
        lookup_id = require_int (request.vars.get ('id'))
        buffer = request.vars.get ('text')
        tool_data = dm.get ('dev_tools', lookup_id)
        dev_save_code (tool_data.filename, buffer)
    elif request.args[0] == 'delete':
        raise NotImplementedError ()
    elif request.args[0] == 'publish':
        lookup_id = int (request.vars.get ('id'))
        dm.unlink ('dev_tools', lookup_id)
        dm.public ('tools', lookup_id, True)
    elif request.args[0] == 'fork':
        raise NotImplementedError ()

def tool():
    user_id = require_logged_in ()
    if request.args[0] == 'read':
        lookup_id = require_int (request.vars.get ('id'))
        tool_data = dm.get ('tools', lookup_id)
        buffer = dev_read_code (tool_data.filename)
        buffer = dev_format_code (buffer)
        val = tool_data.public ()
        val['text'] = buffer
        return json.dumps (val)
    elif request.args[0] == 'args':
        lookup_id = require_int (request.vars.get ('id'))
        return json.dumps (get_tool (lookup_id)['args'])
    elif request.args[0] == 'run':
        lookup_id = require_int (request.vars.get ('id'))
        m = get_tool (lookup_id)
        if m['python']:
            return call_py (m).json ()
        else:
            return call_r (m).json ()

def result():
    if request.args[0] == 'load':
        lookup_id = int (request.vars.get ('id'))
        result = dm.get ('results', lookup_id)
        file = open ('applications/' + request.application + '/tool/results/' + result.filename, 'r')
        response.headers['Content-Type'] = result.type
        buffer = file.read ()
        buffer = sub ('width="[^"]+"', '', buffer, 1)
        buffer = sub ('height="[^"]+"', '', buffer, 1)
        return buffer
    elif request.args[0] == 'save':
        require_logged_in ()
        lookup_id = int (request.vars.get ('id'))
        name = require_text (request.vars.get ('name'))
        dm.update ('results', lookup_id, name = name)
        dm.link ('results', lookup_id)
        return dm.get ('results', lookup_id).json ()
    elif request.args[0] == 'publish':
        require_logged_in ()
        perm = boolean (require_int (request.vars.get ('perm')))
        lookup_id = int (request.vars.get ('id'))
        dm.update ('results', lookup_id, public = perm)

def analysis():
    if request.args[0] == 'save':
        require_logged_in ()
        lookup_id = int (request.vars.get ('id'))
        name = require_text (request.vars.get ('name'))
        tool_data = dm.get ('tools', lookup_id)
        data = format_analysis (request.vars, lookup_id)
        id = dm.insert ('analyses', tool = dm.get ('tools', lookup_id).json (), name = name, json = data)
        dm.link ('analyses', id)
        return dm.get ('analyses', id).json ()
    elif request.args[0] == 'load':
        raise NotImplementedError ()
    elif request.args[0] == 'publish':
        raise NotImplementedError ()
