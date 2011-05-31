from re import match
from gluon.contrib.login_methods.email_auth import email_auth
#from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount

from gluon.tools import *
auth = Auth(globals(), db)                     

auth.define_tables()                          

auth.settings.create_user_groups = False
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.register_next = URL (a = request.application, c = 'default',  f = 'register')
auth.settings.login_next = URL (a = request.application, c = 'default',  f = 'index.html')

auth.settings.login_methods.append(
    email_auth("smtp.gmail.com:587", "@gmail.com"))
#auth.settings.login_form = GaeGoogleAccount ()

try:
    admin_role = auth.id_group ("Administrator")
    dev_role = auth.id_group ("Developer")
    auth_role = auth.id_group ("Authenticated")
except:
    admin_role = None
    dev_role = None
    auth_role = None

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

def check_logged_in ():
    if not auth.user:
        return False
    return True

def check_role (role):
    if not auth.user:
        False
    if auth.has_membership (admin_role, auth.user.id):
        return True
    if not auth.has_membership (role, auth.user.id):
        return False
    return True

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
