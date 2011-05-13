from re import match

def require_logged_in ():
    if not auth.user:
        raise HTTP (401, "Login Required")
    return auth.user.id

def require_user (owner):
    if not auth.user:
        raise HTTP (401, "Login Required")
    if not auth.user.id == owner:
        raise HTTP (401, "Permission Denied")
    return auth.user.id

def require_role (role):
    if not auth.user:
        raise HTTP (401, "Login Required")
    if auth.has_membership (admin_role, auth.user.id):
        return auth.user.id
    if not auth.has_membership (role, auth.user.id):
        raise HTTP (401, "Permission Denied")
    return auth.user.id

def require_val (input):
    if not input:
        raise HTTP (400, 'Missing Parameter')
    return input

def require_alphanumeric (input):
    if not match ('^[a-zA-z0-9_]*$', input):
        raise HTTP (400, 'Bad Character In Request')
    return input

def require_int (input):
    if not match ('^[0-9]*$', input):
        raise HTTP (400, 'Bad Character In Request')
    return int (input)
