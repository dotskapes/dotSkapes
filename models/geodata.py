map_model = DM_TableModel (DM_Field ('name', 'string', required = True, title = True, text = 'Name'),
                           DM_Field ('prefix', 'string', default = '', visible = False),
                           DM_Field ('filename', 'string', required = True, visible = False),
                           DM_Field ('src', 'string', required = True, visible = True),
                           DM_Field ('styles', 'string', default = '', visible = False),
                           name = 'Maps',
)

dm.define_datatype ('maps', map_model)
