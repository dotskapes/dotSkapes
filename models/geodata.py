map_model = DM_TableModel (DM_Field ('name', 'string', required = True, title = True, text = 'Name'),
                           DM_Field ('prefix', 'string', default = '', visible = False),
                           DM_Field ('filename', 'string', required = True, visible = False),
                           DM_Field ('src', 'string', required = True, visible = True),
                           DM_Field ('styles', 'string', default = '', visible = False),
                           name = 'Maps',
)

dm.define_datatype ('maps', map_model)

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
