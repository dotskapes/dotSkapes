def data():
    return {'data': get_datatypes ()}

def tree():
    return {'data': get_datatypes ()}

def grid():
    return {'data': get_datatypes ()}

def base():
    return {
        'dev_role': check_role (dev_role),
        'admin_role': check_role (admin_role),        
        }
