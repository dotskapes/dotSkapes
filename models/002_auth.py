import re
from re import match
from gluon.contrib.login_methods.email_auth import email_auth
#from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount

from gluon.tools import *
auth = Auth(globals(), db)                     

auth.define_tables()                          

auth.settings.create_user_groups = False
auth.settings.actions_disabled = ['request_reset_password']
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.register_next = URL (a = request.application, c = 'default',  f = 'user')
auth.settings.login_next = URL (scheme = 'http', a = request.application, c = 'default',  f = 'index.html')

auth.settings.login_methods.append(
    email_auth("smtp.gmail.com:587", "@gmail.com"))
#auth.settings.login_form = GaeGoogleAccount ()

try:
    admin_role = auth.id_group ("Administrator")
    dev_role = auth.id_group ("Developer")
    auth_role = auth.id_group ("Authenticated")
    writer_role = auth.id_group ("Writer")
    editor_role = auth.id_group ("Editor")
except:
    admin_role = None
    dev_role = None
    auth_role = None
    writer_role = None
    editor_role = None

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
    if not check_role (role):
        raise HTTP (401, "Permission Denied")
    else:
        return auth.user.id

def check_logged_in ():
    if not auth.user:
        return False
    return auth.user.id

def check_user (user_id):
    if not auth.user:
        return False
    return auth.user.id == user_id

def check_role (role):
    if not auth.user:
        return False
    if auth.has_membership (admin_role, auth.user.id):
        return True
    if role == writer_role and auth.has_membership (editor_role, auth.user.id):
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

def require_hex (input):
    if not match ('^[0-9a-fA-F]*$', input, re.U):
        raise HTTP (400, 'Bad Character In Request: %s' % input)
    return str (input)

def require_decimal (input):
    if not match ('^-?[0-9]*\.?[0-9]*$', input):
        raise HTTP (400, 'Bad Character In Request')
    return int (input)

def require_color (input):
    from savage.graphics.color import hex_to_color
    if not match ('^(0x)?[0-9a-fA-F]{6}$', input):
        raise HTTP (400, 'Bad Character In Request')
    return hex_to_color (input)
    
def require_http (input, params = True):
    if not params:
        input = input.split ('?')[0]
    if not match ('^https?://', input):
        input = 'http://' + input
    if input [len (input) - 1] == '/':
        input = input[0:len (input) - 2]
    return input

def require_style_attr (input):
    if not match ('^[a-zA-Z0-9\.%]+$', input, re.U):
        raise HTTP (400, "Bad Character in Request: %s" % input)
    return input

def user_name (id):
    result = db (db[auth.settings.table_user].id == id).select ().first ()
    return result.first_name + ' ' + result.last_name

def require_mongo ():
    if not mongo:
        session['missing'] = 'This page requires MongoDB'
        redirect (URL (r = request, c = 'default', f = 'missing'))
