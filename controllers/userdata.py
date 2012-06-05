def load():
    data_type = require_alphanumeric (request.args[0])
    return dm.load (data_type).json ()

def get():
    data_type = require_alphanumeric (request.args[0])
    data_id = require_alphanumeric (request.vars.get ('id'))
    return dm.get (data_type, data_id).json ()

def append():
    user_id = require_logged_in ()
    data_type = require_alphanumeric (request.args[0])
    data_id = require_int (request.vars.get ('id'))
    return str (dm.link (user_id, data_type, data_id))

def re_init():
    user_id = require_role (admin_role)
    db.datatypes.truncate ()

def tmp_insert():
    user_id = require_role (admin_role)
    data_type = require_alphanumeric (request.args[0])
    request.vars.update ({'owner': user_id})
    return str (dm.insert (data_type, **request.vars))
