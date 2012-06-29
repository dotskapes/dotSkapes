def index():
    return dict()
"""    redirect (URL(r=request,c='default'))  """

def about():
    return dict()

def privacy():
    return dict()

def terms():
    return dict()

def register():
    redirect (URL (r = request, c = 'default', f = 'index'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    from uuid import uuid4
    if deployment_settings.dev_mode.enabled:
        psswd = uuid4 ().hex
        firstname = deployment_settings.dev_mode.firstname
        lastname = deployment_settings.dev_mode.lastname
        email = deployment_settings.dev_mode.email
        auth.get_or_create_user ({'first_name': firstname, 'last_name': lastname, 'email': email, 'password': db.auth_user.password.validate (psswd)[0]})
        db (db[auth.settings.table_user].email == email).update (first_name = firstname, last_name = lastname)
        auth.login_bare (email, psswd)
        redirect  (URL (scheme = 'http', r = request, c = 'default', f = 'index.html'))
    if request.wsgi.environ.get ('wsgi.url_scheme') != 'https':
        redirect (URL (scheme = 'https', args = request.args))
    if request.args (0) == 'logout':
        auth.logout (next = URL (scheme = 'http', r = request, c = 'default', f = 'index.html'))
    elif request.args (0) == 'login':
        if request.vars.has_key ('openid.mode'):
            from openid.consumer import consumer
            from openid.extensions import ax
            cons = session['openid-consumer']
            resp = cons.complete (request.vars, str (request.wsgi.environ['wsgi.url_scheme'] + '://' + request.wsgi.environ['HTTP_HOST'] + request.wsgi.environ['REQUEST_URI']))
            if resp.status == consumer.SUCCESS:
                psswd = uuid4 ().hex
                ax_resp = resp.getSignedNS (ax.FetchRequest.ns_uri)
                email = ax_resp['value.email']
                try:
                    firstname = ax_resp['value.firstname']
                    lastname = ax_resp['value.lastname']
                except:
                    firstname = email
                    lastname = ''
                auth.get_or_create_user ({'first_name': firstname, 'last_name': lastname, 'email': email, 'password': db.auth_user.password.validate (psswd)[0]})
                db (db[auth.settings.table_user].email == email).update (first_name = firstname, last_name = lastname)
                auth.login_bare (email, psswd)
                del session['openid-consumer']
                redirect  (URL (scheme = 'http', r = request, c = 'default', f = 'index.html'))
            elif resp.status == consumer.CANCEL:
                return 'You must allow 3rd party access to login to this site'
            elif resp.status == consumer.FAILURE:
                return 'Login Failed'
        else:
            from openid.consumer.consumer import Consumer
            from openid.store.filestore import FileOpenIDStore
            from openid.extensions import ax
            path = getcwd () + '/applications/' + request.application + '/.openid/'
            store = FileOpenIDStore (path)
            cons = Consumer (session, store)
            req = cons.begin ('https://www.google.com/accounts/o8/id')
            ax_req = ax.FetchRequest ()
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/contact/email', required=True, alias='email'))
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/namePerson/first', required=True, alias='firstname'))
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/namePerson/last', required=True, alias='lastname'))
            req.addExtension (ax_req)
            session['openid-consumer'] = cons

            url = req.redirectURL (str (request.wsgi.environ['wsgi.url_scheme'] + '://' + request.wsgi.environ['HTTP_HOST']), return_to = str (request.wsgi.environ['wsgi.url_scheme'] + '://' + request.wsgi.environ['HTTP_HOST'] + request.wsgi.environ['REQUEST_URI']))

            redirect (url)
    else:
        raise HTTP (400, "Bad Request")

def missing():
    return {'message': session['missing']}
