from re import match

from gluon.tools import *
auth = Auth(globals(), db)                     

auth.define_tables()                          

auth.settings.create_user_groups = False
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.register_next = URL (a = request.application, c = 'default',  f = 'register')
auth.settings.login_next = URL (a = request.application, c = 'default',  f = 'index.html')

table = auth.settings.table_group
if not db(db[table].id > 0).count():
    admin_role = auth.add_group ("Administrator", "System Administrator - can access & make changes to any data")
    dev_role = auth.add_group ("Developer", "Developer - Users with development privileges")
    auth_role = auth.add_group ("Authenticated", "Authenticated - all logged-in users")
else:
    admin_role = auth.id_group ("Administrator")
    dev_role = auth.id_group ("Developer")
    auth_role = auth.id_group ("Authenticated")

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

def require_text (input):
    if not match ('^[a-zA-z0-9_ ]*$', input):
        raise HTTP (400, 'Bad Character In Request')
    return input

def require_int (input):
    if not match ('^[0-9]*$', input):
        raise HTTP (400, 'Bad Character In Request')
    return int (input)
