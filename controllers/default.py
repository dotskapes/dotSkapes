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
    response.title = 'skapes'
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
            '''params = {
                'openid.ns.ui': 'http://specs.openid.net/extensions/ui/1.0',
                'ui.mode': 'popup',
                'openid.ui.icon': 'true',
                'openid.ns.ax': 'http://openid.net/srv/ax/1.0',
                'openid.ax.mode': 'fetch_request',
                'openid.ax.type.email': 'http://axschema.org/contact/email',
                'openid.ax.type.firstname': 'http://axschema.org/namePerson/first',
                'openid.ax.type.lastname': 'http://axschema.org/namePerson/last',
                'openid.ax.required': 'email,firstname,lastname',
            }
            session['openid-consumer'] = cons
            url = req.redirectURL ('https://zk.healthscapes.org', return_to = 'https://zk.healthscapes.org/healthscapes/default/user/login')
            for key, value in params.iteritems ():
                url += '&%s=%s' % (key, value)'''
            ax_req = ax.FetchRequest ()
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/contact/email', required=True, alias='email'))
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/namePerson/first', required=True, alias='firstname'))
            ax_req.add (ax.AttrInfo (type_uri='http://axschema.org/namePerson/last', required=True, alias='lastname'))
            req.addExtension (ax_req)
            session['openid-consumer'] = cons
            url = req.redirectURL ('https://zk.healthscapes.org', return_to = 'https://zk.healthscapes.org/healthscapes/default/user/login')
            redirect (url)
        '''if request.vars.has_key ('openid.mode'):
            if request.vars['openid.mode'] == 'cancel':
                raise HTTP (400, "Access Denied")
            params = {
                'openid.assoc_handle': request.vars ['openid.assoc_handle'],
                'openid.signed': request.vars['openid.signed'],
                'openid.sig': request.vars['openid.sig'],
                'openid.mode': 'check_authentication',
                'openid.response_nonce': request.vars ['openid.response_nonce'],
            }
            for item in request.vars['openid.signed'].split (','):
                params.update ({'openid.%s' % item: request.vars['openid.%s' % item]})
                xrds = BeautifulStoneSoup (urlopen ('https://www.google.com/accounts/o8/id').read ())
                endpoint = xrds.find ('uri').string
                response.headers['Content-Type'] = 'text'
            valid = urlopen (endpoint, urlencode (params)).read ()
            if valid == 'is_valid:true\n':
                psswd = uuid4 ().hex
                auth.get_or_create_user ({'first_name': request.vars['openid.ext1.value.firstname'], 'last_name': request.vars['openid.ext1.value.lastname'], 'email': request.vars['openid.ext1.value.email'], 'password': db.auth_user.password.validate (psswd)[0]})
                auth.login_bare (request.vars['openid.ext1.value.email'], psswd)
                redirect  (URL (scheme = 'http', r = request, c = 'default', f = 'index.html'))
            else:
                raise HTTP (400)
        else:
            xrds = BeautifulStoneSoup (urlopen ('https://www.google.com/accounts/o8/id').read ())
            endpoint = xrds.find ('uri').string
            params = {
                'openid.mode': 'checkid_setup',
                'openid.ns': 'http://specs.openid.net/auth/2.0',
                'openid.return_to': 'https://zk.healthscapes.org/healthscapes/default/user/login',
                'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
                'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
                'openid.realm': 'https://zk.healthscapes.org',
                #'openid.ns.pape': 'http://specs.openid.net/extensions/pape/1.0',
                'openid.ns.ui': 'http://specs.openid.net/extensions/ui/1.0',
                #'openid.ui.mode': 'popup',
                'openid.ui.icon': 'true',
                'openid.ns.ax': 'http://openid.net/srv/ax/1.0',
                'openid.ax.mode': 'fetch_request',
                'openid.ax.type.email': 'http://axschema.org/contact/email',
                'openid.ax.type.firstname': 'http://axschema.org/namePerson/first',
                'openid.ax.type.lastname': 'http://axschema.org/namePerson/last',
                'openid.ax.required': 'email,firstname,lastname',
            }
            redirect (endpoint + '?' + urlencode (params))'''
    else:
        raise HTTP (400, "Bad Request")


'''def google():
    from openid.consumer.consumer import Consumer
    from openid.store.filestore import FileOpenIDStore
    path = getcwd () + '/applications/' + request.application + '/tmp/'
    store = FileOpenIDStore (path)
    cons = Consumer (session, store)
    req = cons.begin ('https://www.google.com/accounts/o8/id')
    params = {
        #'openid.mode': 'checkid_setup',
        #'openid.ns': 'http://specs.openid.net/auth/2.0',
        #'return_to': 'https://zk.healthscapes.org/healthscapes/default/user/login',
        #'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        #'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        #'openid.realm': 'https://zk.healthscapes.org',
        #'ns.pape': 'http://specs.openid.net/extensions/pape/1.0',
        'openid.ns.ui': 'http://specs.openid.net/extensions/ui/1.0',
        'ui.mode': 'popup',
        'openid.ui.icon': 'true',
        'openid.ns.ax': 'http://openid.net/srv/ax/1.0',
        'openid.ax.mode': 'fetch_request',
        'openid.ax.type.email': 'http://axschema.org/contact/email',
        'openid.ax.type.firstname': 'http://axschema.org/namePerson/first',
        'openid.ax.type.lastname': 'http://axschema.org/namePerson/last',
        'openid.ax.required': 'email,firstname,lastname',
    }
    #for key, value in params.iteritems ():
    #    req.addExtensionArg ('', key, value)
    #req.addExtensionArg ('openid.ns', 'ax', 'http://openid.net/srv/ax/1.0')
    #req.addExtensionArg ('openid.ax', 'mode', 'fetch_request')
    #req.addExtensionArg ('openid.ax.type', 'email', 'http://axschema.org/contact/email')
    #req.addExtensionArg ('openid.ax.type', 'firstname', 'http://axschema.org/contact/firstname')
    #req.addExtensionArg ('openid.ax.type', 'lastname', 'http://axschema.org/contact/lastname')
    #req.addExtensionArg ('openid.ax', 'required', 'email,firstname,lastname')
        #'ax.mode': 'fetch_request',
        #'#ax.type.email': 'http://axschema.org/contact/email',
        #'ax.type.firstname': 'http://axschema.org/namePerson/first',
        #'ax.type.lastname': 'http://axschema.org/namePerson/last',
        #'ax.required': 'email,firstname,lastname',

    session['openid-consumer'] = cons
    url = req.redirectURL ('https://zk.healthscapes.org', return_to = 'https://zk.healthscapes.org/healthscapes/default/google_complete')
    for key, value in params.iteritems ():
        url += '&%s=%s' % (key, value)
    redirect (url)
        
def google_complete():
    from openid.consumer import consumer
    cons = session['openid-consumer']
    #str (request.wsgi.environ['wsgi.url_scheme'] + '://' + request.wsgi.environ['HTTP_HOST'] + request.wsgi.environ['REQUEST_URI']
    resp = cons.complete (request.vars, str (request.wsgi.environ['wsgi.url_scheme'] + '://' + request.wsgi.environ['HTTP_HOST'] + request.wsgi.environ['REQUEST_URI']))
    if resp.status == consumer.SUCCESS:
        return request.vars.get ('openid.ext1.value.email')
'''
