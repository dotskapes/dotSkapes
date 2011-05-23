def index():
    if auth.user:
        user_id = auth.user.id
    else:
        user_id = None
    output = {}
    output.update ({'geoserver': deployment_settings.geoserver})
    if user_id:
        output.update ({'side_bar': True, 'tool_list': dm.local_load ('tools').json (), 'tool_saved_results': dm.local_load ('results').json (), 'tool_saved_analyses': dm.local_load ('analyses').json (), 'maps_saved': dm.local_load ('maps').json ()})
        if auth.has_membership ('Developer', auth.user.id):
            output.update ({'dev_tools': True, 'in_dev': dm.local_load ('dev_tools').json ()})
        else:
            output.update ({'dev_tools': False})
    else:
        output.update ({'side_bar': False, 'dev_tools': False})
    response.title = 'Healthscapes'
    return(output)

def register():
    if auth.user:
        table = auth.settings.table_user_name
        if db(db[table].id > 0).count() == 1:
            auth.add_membership (admin_role, auth.user.id)
            auth.add_membership (dev_role, auth.user.id)
        else:
            auth.add_membership (auth_role, auth.user.id)
    redirect (URL (a = request.application, c = 'default',  f = 'index.html'))

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
    form = auth ()
    '''if request.args[0] == 'register':
        if form.accepts (request.vars):
            table = auth.settings.table_user_name
            if db(db[table].id > 0).count() == 1:
                auth.add_membership (admin_role, auth.user_id)
            else:
                auth.add_membership (auth_role, auth.user.id)'''
    return dict(form=form)
