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
        lookup_id = require_alphanumeric (request.vars.get ('id'))
        if request.vars.has_key ('tmp'):
            buffer = session[lookup_id]['buffer']
            response.headers['Content-Type'] = session[lookup_id]['type']
        else:
            result = dm.get ('results', lookup_id)
            file = open ('applications/' + request.application + '/tool/results/' + result.filename, 'r')
            response.headers['Content-Type'] = result.type
            buffer = file.read ()
        buffer = sub ('width="[^"]+"', '', buffer, 1)
        buffer = sub ('height="[^"]+"', '', buffer, 1)
        return buffer
    elif request.args[0] == 'save':
        require_logged_in ()
        tmp_lookup = require_alphanumeric (request.vars.get ('id'))
        file_id = str (uuid4 ().int)
        file = open ('applications/' + request.application + '/tool/results/' + file_id, 'w')
        file.write (session[tmp_lookup]['buffer'])
        file.close ()
        r_type = session[tmp_lookup]['type']
        name = require_text (request.vars.get ('name'))
        #dm.update ('results', lookup_id, name = name)
        lookup_id = dm.insert ('results', name = name, filename = file_id, type = r_type)
        dm.link ('results', lookup_id)
        return dm.get ('results', lookup_id).json ()
    elif request.args[0] == 'publish':
        require_logged_in ()
        perm = boolean (require_int (request.vars.get ('perm')))
        lookup_id = int (request.vars.get ('id'))
        dm.update ('results', lookup_id, public = perm)
        return str (perm)
    elif request.args[0] == 'export_available':
        require_logged_in ()
        lookup_id = require_int (request.vars.get ('id'))
        r_type = dm.get ('results', lookup_id).type
        if r_type == mime.PNG:
            return json.dumps ([{'name': 'png', 'id': mime.PNG}])
        elif r_type == mime.SVG:
            return json.dumps ([{'name': 'svg', 'id': mime.SVG}, {'name': 'png', 'id': mime.PNG}])
        elif r_type == mime.HTML:
            return json.dumps ([{'name': 'html', 'id': mime.HTML}])
    elif request.args[0] == 'export':
        from urllib import unquote
        require_logged_in ()
        lookup_id = require_int (request.vars.get ('id'))
        export_type = request.vars.get ('mode')
        export_type = unquote (export_type)
        filename = require_alphanumeric (request.vars.get ('filename'))
        result = dm.get ('results', lookup_id)
        r_type = result.type
        if r_type == export_type:
            file = open ('applications/' + request.application + '/tool/results/' + result.filename, 'r')
            buffer = file.read ()
            response.headers['Content-Type'] = result.type
            response.headers['Content-Disposition'] = 'attachment; filename="' + filename + mime_ext (export_type) + '"'
            return buffer
        elif export_type == mime.PNG and r_type == mime.SVG:
            import rsvg
            import cairo
            from tempfile import NamedTemporaryFile as TF
           
            file = open ('applications/' + request.application + '/tool/results/' + result.filename, 'r')
            buffer = file.read ()
            file2 = TF ()
            file2.write (buffer)
            file2.seek (0)
            svg = rsvg.Handle (file = file2.name)

            surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, int (800), int (600))
            context = cairo.Context (surface)
            svg.render_cairo (context)

            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Disposition'] = 'attachment; filename="' + filename + mime_ext (export_type) + '"'
            
            surface.write_to_png (response.body)
            return response.body.getvalue ()
        else:
            raise HTTP (400)

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
