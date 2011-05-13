def get_datatypes ():
    datatypes = {}
    keys = dm.get_types ()
    for k in keys:
        datatypes[k] = dm.get_fields (k)
    return datatypes
