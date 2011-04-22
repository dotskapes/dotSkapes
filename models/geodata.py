db.define_table ('saved_maps',
                 Field ('user_id', 'integer', default = None),
                 Field ('json', 'string'))

def load_maps(userid):
    if userid is None:
        raise HTTP (400)
    result = db (db.saved_maps.user_id == userid).select ()
    if len (result) == 0:
        db.saved_maps.insert (user_id = userid, json = '{}')
        return '{}'
    else:
        return result[0].json
