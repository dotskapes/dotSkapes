dm.define_datatype ('maps', 
    DM_Field (
        Field ('name', 'string', required = True),
        DM_Settings (), 
        DisplaySettings (title = True, name = 'Name')),
    DM_Field (
        Field ('prefix', 'string', default = ''),
        DM_Settings (), 
        DisplaySettings (visible = False)),
    DM_Field (
        Field ('filename', 'string', required = True),
        DM_Settings (), 
        DisplaySettings (visible = False)),
    DM_Field (
        Field ('type', 'string', required = True),
        DM_Settings (), 
        DisplaySettings (visible = False)),   
)

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
