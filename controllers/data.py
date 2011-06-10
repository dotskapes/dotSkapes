def save():
    datatype = require_alphanumeric (request.args[0])
    lookup_id = require_int (request.vars.get ('id'))
    dm.link (datatype, lookup_id)

def load():
    datatype = require_alphanumeric (request.args[0])
    if len (request.args) > 1 and request.args[1]:
        kw = require_alphanumeric (request.args[1])
        rec = boolean (request.vars.get ('recommend'))
        if not rec:
            return '{data: ' + dm.global_load (datatype, [kw]).json () + '}'
        else:
            result = db.executesql ('''
            SELECT keyword.kw, counts.counts 
            FROM (SELECT keycount.kw_id, keycount.counts 
               FROM (SELECT id 
                  FROM disease 
                  WHERE d = '%s') AS diseases
               INNER JOIN keycount
               ON keycount.d_id = diseases.id) AS counts
            INNER JOIN keyword
            ON keyword.id = counts.kw_id;
            ''' % (kw,))

            lookup = set ()
            def reducer (item):
                if item['id'] in lookup:
                    return False
                else:
                    lookup.add (item['id'])
                    return True

            rList = dm.load_keyworded (datatype, kw)
            for item in rList:
                lookup.add (item['id'])

            for r in result:
                val = r[0]
                next = dm.load_keyworded (datatype, val)
                filtered = filter (reducer, next)
                rList += filtered
            return '{data:' + rList.json () + '}'
    else:
        return '{data: ' + dm.global_load (datatype).json () + '}'

def unlink():
    datatype = require_alphanumeric (request.args[0])
    lookup_id = require_int (request.vars.get ('id'))
    dm.unlink (datatype, lookup_id)
