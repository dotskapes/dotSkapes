def boolean (val):
    if isinstance (val, str):
        lower = val.lower ()
        if lower == 'false':
            return False
        elif lower == 'f':
            return False
        elif lower == 'true':
            return True
        elif lower == 't':
            return True
    elif isinstance (val, int):
        if val == 0:
            return False
        elif val == 1:
            return True
    elif isinstance (val, float):
        if val == 0.0:
            return False
        elif val == 1.0:
            return True
    else:
        if val is None:
            return False
    raise RuntimeError ('Cast to boolean failed: Could not convert ' +
                        str (val) + ' to a boolean')


def load():
    data_type = require_alphanumeric (request.args[0])
    if len (request.args) > 1 and request.args[1]:
        kw = require_alphanumeric (request.args[1])
        rec = boolean (request.vars.get ('recommend'))
        if not rec:
            return dm.load_keyworded (data_type, kw).json ()
        else:
            result = db.executesql ('''
            SELECT keyword.kw, counts.count 
            FROM (SELECT keycount.kw_id, keycount.count 
               FROM (SELECT id 
                  FROM disease 
                  WHERE d = '%s') AS diseases
               INNER JOIN keycount
               ON keycount.d_id = diseases.id) AS counts
            INNER JOIN keyword
            ON keyword.id = counts.kw_id;
            ''' % (kw,))
            rList = dm.load_keyworded (data_type, kw)
            for r in result:
                val = r[0]
                next = dm.load_keyworded (data_type, val)
                for n in next:
                    rList.append (n)
            return rList.json ()
    else:
        return dm.load_public (data_type).json ()
