def index():
    output = {}
    if check_logged_in ():
        output.update ({'side_bar': True, 'tool_list': dm.local_load ('tools').json (), 'tool_saved_results': dm.local_load ('results').json (), 'tool_saved_analyses': dm.local_load ('analyses').json (), 'maps_saved': dm.local_load ('maps').json ()})
        if check_role (dev_role):
            output.update ({'dev_tools': True, 'in_dev': dm.local_load ('dev_tools').json ()})
        else:
            output.update ({'dev_tools': False})
    else:
        output.update ({'side_bar': False, 'dev_tools': False})
    response.title = 'Healthscapes'
    return(output)

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
                firstname = ax_resp['value.firstname']
                lastname = ax_resp['value.lastname']
                auth.get_or_create_user ({'first_name': firstname, 'last_name': lastname, 'email': email, 'password': db.auth_user.password.validate (psswd)[0]})
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
