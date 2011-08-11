db.define_table('keyword',
    Field('kw', 'string', length = 512),
)

db.define_table('disease',
    Field('d', 'string', length = 512),
)

db.define_table('keycount',
    Field('kw_id', 'integer'),
    Field('d_id', 'integer'),
    Field('counts','integer'),
)

def add_keyword (*argv):
    from re import sub
    kw = argv[0]
    #file = open ('applications/' + request.application + '/diseases/' + kw + '/output.frq')
    file = open (argv[1])
    string = file.read ()
    result = db.executesql ('''
        SELECT id FROM disease WHERE d = '%s'
    ''' % kw)
    if len (result) == 0:
        d_id = db.disease.insert (d = kw)
    else:
        d_id = result[0][0]
    words = string.split (';')
    for w in words:
        m = w.split (' ')
        if len (m) != 2:
            continue
        key = m[0]
        val = int (m[1])
        key = sub ('([\'\"\\\])', '\\\\1', key)
        result2 = db.executesql ('''
            SELECT id FROM keyword WHERE kw = '%s'
        ''' % key)
        if len (result2) == 0:
            kw_id = db.keyword.insert (kw = key)
        else:
            kw_id = result2[0][0]        
        result3 = db.executesql ('''
            SELECT id FROM keycount WHERE kw_id = %d AND d_id = %d
        ''' % (kw_id, d_id))
        print "Adding: " + key + " (" + str (kw_id) + ")"
        if len (result3) == 0:
            result3 = db.executesql ('''
                INSERT INTO keycount (kw_id, d_id, counts)
                VALUES (%d, %d, %d)
            ''' % (kw_id, d_id, val))
        else:
            result3 = db.executesql ('''
                UPDATE keycount 
                SET counts = %d
                WHERE kw_id = %d AND d_id = %d
            ''' % (val, kw_id, d_id))
    return


def tmp_create_lit ():
    return
    db.keyword.truncate ()
    db.disease.truncate ()
    db.keycount.truncate ()
    #m_key = db.keyword.insert (kw ='malaria')
    #p_key = db.keyword.insert (kw = 'precipitation')
    #s_key = db.keyword.insert (kw = 'tiger_roads')
    #m = db.disease.insert (d = 'malaria')
    #db.keycount.insert (kw_id = m_key, d_id = m, count = 100)
    #db.keycount.insert (kw_id = p_key, d_id = m, count = 67)
    #db.keycount.insert (kw_id = s_key, d_id = m, count = 42)
