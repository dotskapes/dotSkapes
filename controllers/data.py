def save():
    datatype = require_alphanumeric (request.args[0])
    lookup_id = require_alphanumeric (request.vars.get ('id'))
    dm.link (datatype, lookup_id)
    return dm.get (datatype, lookup_id).json ()

def load():
    datatype = require_alphanumeric (request.args[0])
    if len (request.args) > 1 and request.args[1]:
        kw = require_alphanumeric (request.args[1])
        rec = boolean (request.vars.get ('recommend'))
        if not rec:
            return '{data: ' + dm.global_load (datatype, [kw]).json () + '}'
        else:
            result = mongo.words.find ({'word': kw})
            if not result.count ():
                return '{data:[]}'
            keys = result[0]['kw'].items ()
            keys.sort (key = lambda x: x[1])
            keys.reverse ()
            top = len (keys) / 4
            words = map (lambda x: x[0], keys[0:top])
            return '{data: ' + dm.global_load (datatype, words).json () + '}'
    else:
        return '{data: ' + dm.global_load (datatype).json () + '}'

def unlink():
    datatype = require_alphanumeric (request.args[0])
    lookup_id = require_alphanumeric (request.vars.get ('id'))
    dm.unlink (datatype, lookup_id)

def tag():
    datatype = require_alphanumeric (request.args[0])
    lookup_id = require_alphanumeric (request.vars.get ('id'))
    kw = require_alphanumeric (request.vars.get ('kw'))
    dm.tag (datatype, lookup_id, [kw])
