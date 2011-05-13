db.define_table('keyword',
    Field('kw'),
)

db.define_table('disease',
    Field('d'),
)

db.define_table('keycount',
    Field('kw_id', db.keyword),
    Field('d_id', db.disease),
    Field('count','integer'),
)

def tmp_create_lit ():
    db.keyword.truncate ()
    db.disease.truncate ()
    db.keycount.truncate ()
    m_key = db.keyword.insert (kw ='malaria')
    p_key = db.keyword.insert (kw = 'precipitation')
    s_key = db.keyword.insert (kw = 'tiger_roads')
    m = db.disease.insert (d = 'malaria')
    db.keycount.insert (kw_id = m_key, d_id = m, count = 100)
    db.keycount.insert (kw_id = p_key, d_id = m, count = 67)
    db.keycount.insert (kw_id = s_key, d_id = m, count = 42)
