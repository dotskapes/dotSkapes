def parse_wiki_rest ():
    rest_vars = attr_dict ()
    rest_vars.wiki_mode = request.function
    if request.args (1):
        rest_vars.page_slug = request.args (0)
        rest_vars.page_op = request.args (1)
    else:
        rest_vars.page_slug = None
        rest_vars.page_op = request.args (0)
    if request.args (3):
        rest_vars.comment_id = request.args (2)
        rest_vars.comment_op = request.args (3)
    else:
        rest_vars.comment_id = None
        rest_vars.comment_op = request.args (2)
    #rest_vars.repr = get_representation ()
    return rest_vars

def render_page ():
    rest_vars = parse_wiki_rest ()
    #arg, repr = get_arg (request.args (0))
    if not rest_vars.page_op and not rest_vars.page_slug:
        return render_index (rest_vars)
    elif rest_vars.page_op == 'create':
        if not rest_vars.page_slug:
            return render_create (rest_vars)
        else:
            return create_page (rest_vars)
    elif rest_vars.page_op == 'edit':
        return render_edit (rest_vars)
    elif rest_vars.page_op == 'view':
        return render_view (rest_vars)
    elif rest_vars.page_op == 'publish':
        return render_publish (rest_vars)
    elif rest_vars.page_op == 'unpublish':
        return render_unpublish (rest_vars)
    elif rest_vars.page_op == 'delete_confirm':
        return render_delete_confirm (rest_vars)
    elif rest_vars.page_op == 'delete':
        return render_delete (rest_vars)
    elif rest_vars.page_op == 'categories':
        return render_categories (rest_vars)
    elif rest_vars.page_op == 'comment':
        return render_comment (rest_vars)
    else:
        raise HTTP (400, "Bad Blog Operation")

def render_comment (rest_vars):
    if rest_vars.comment_op == 'create':
        render_comment_create (rest_vars)
    elif rest_vars.comment_op == 'delete':
        render_comment_delete (rest_vars)
    else:
        raise HTTP (400, "Bad Comment Operation")

def render_index (rest_vars):
    response.view = 'wiki/index.html'
    from re import finditer
    if check_role (editor_role):
        p_query = {}
    elif check_role (writer_role):
        '''p_query = {
            '$not': {
                'public': {'$ne' : True},
                'owner': {'$ne' : auth.user.id},
                }
                }''' 
        p_query = {
            '$or': [
                {'public': True}, 
                {'owner': auth.user.id}
                ]
            }
    else:
        p_query = {'public': True}
    term = request.vars.get ('search')
    if term:
        '''m_query = {
            '$or': [
                {'body': {'$regex': re.compile ('%s' % term)}},
                {'title': {'$regex': re.compile ('%s' % term)}},
                ]
            }'''
        '''m_query = {
            '$not': {
                'body': {'$not': re.compile ('%s' % term)},
                'title': {'$not': re.compile ('%s' % term)},
                }
            }'''
        m_query = {'body': re.compile ('%s' % term)}
        '''query = {
            '$nor': [
                {
                    'body': {'$not': re.compile ('%s' % term)},
                    'title': {'$not': re.compile ('%s' % term)},
                    },
                {
                    '$not': query,
                    }
                ]
            }'''
    else:
        m_query = {}
    rf = request.function
    if rf == 'blog':
        cats = map (lambda x: x._id, MongoWrapper (mongo.categories.find ({'blog': True})))
    elif rf == 'case':
        cats = map (lambda x: x._id, MongoWrapper (mongo.categories.find ({'case': True})))
    elif rf == 'docs':
        cats = map (lambda x: x._id, MongoWrapper (mongo.categories.find ({'docs': True})))
    elif rf == 'tutorials':
        cats = map (lambda x: x._id, MongoWrapper (mongo.categories.find ({'tutorial': True})))
    else:
        raise HTTP (400, "Bad Category")
    c_query = {
        'categories': {
            '$in': cats,
            },
        }
    query = {
        '$and': [
            p_query,
            m_query,
            c_query,
            ]
        }
    pages = MongoCursorWrapper (mongo.blog.find (query).sort ('date', pymongo.DESCENDING))
                
    if request.vars.has_key ('start'):
        start = require_int (request.vars.get ('start'))
    else:
        start = 0

    if request.vars.has_key ('max'):
        max_ret = require_int (request.vars.get ('max'))
    else:
        max_ret = 10

    first = (start + max_ret >= pages.count ())
    last = (start == 0)

    older = {}
    older.update (request.vars)
    older['start'] = start + max_ret

    newer = {}
    newer.update (request.vars)
    newer['start'] = start - max_ret

    pages = pages[start:(start + max_ret)]
    for p in pages:
        start = 0
        widgets = {}
        strings = []
        p.body = sub ('%', '&#37;', p.body)
        p.body = sub ('\n', '\n ', p.body)
        for i, widget in enumerate (finditer ('``([^`]|(`(?!`)))*``:widget', p.body)):
            strings.append (p.body[start:widget.start (0)])
            key = 'widget_' + str (i)
            strings.append ('%(' + key +')s')
            widgets[key] = p.body[widget.start (0):widget.end (0)]
            start = widget.end (0)
        strings.append (p.body[start:])
        
        words = (''.join (strings)).split (' ')
        if len (words) > 300:
            p.more = True
            p.body = ' '.join (words[0:299])
        else:
            p.more = False
            p.body = ' '.join (words)
        p.body = p.body % widgets
        p.body = sub ('&#37;', '%', p.body)
        p.body = sub ('\n ', '\n', p.body)
        p.cats = []

    return dict(pages = pages, first = first, last = last, older = older, newer = newer)

def render_create (rest_vars):
    require_role (writer_role)
    response.view = 'wiki/create.html'
    return {}

def render_edit (rest_vars):
    response.view = 'wiki/edit.html'
    page = load_page (rest_vars.page_slug)
    require_page_authorized (page)
        
    if request.vars.get ('create'):
        create = True
    else:
        create = False
        
    if request.vars.has_key ('slug'):
        new_slug = request.vars.get ('slug')
        if page.slug != new_slug:
            if (len (new_slug) == 0) or mongo.blog.find ({'slug': new_slug}).count ():
                response.flash = 'URL Already Exists'
                return dict (page = request.vars, create = create)
        vars = request.vars
        cats = json.loads (request.vars.get ('cats')) 
        mongo.blog.update ({'slug': page.slug}, {'$set': {
                    'slug': vars.slug,
                    'title': vars.title,
                    'public': vars.public == 'on',
                    'body': vars.body,
                    'categories': map (lambda x: ObjectId (x), cats),
                    'tags': json.loads (request.vars.get ('tags')),
                    }})
        redirect (URL (r = request, args = [vars.slug, 'view']))
    else:
        return dict (page = page, create = create)

def render_view (rest_vars):
    response.view = 'wiki/view.html'
    page = load_page (rest_vars.page_slug)
    return dict(page = page)

def create_page (rest_vars):
    require_role (writer_role)
    if mongo.blog.find ({'slug': rest_vars.page_slug}).count () > 0:
        response.flash = 'Slug already exists'
        return render_create (rest_vars)
    else:
        import datetime
        slug = rest_vars.page_slug
        pid = mongo.blog.insert ({
                'slug': slug,
                'title': '',
                'comments': [],
                'public': True,
                'owner': auth.user.id,
                'body': '',
                'tags': [],
                'categories': [],
                'date': format_datetime_blog (datetime.datetime.now ())})
        mongo.blog.ensure_index ('slug')
        redirect (URL (r = request, args = [slug, 'edit'], vars = {'create': True}))

def format_datetime_blog (date_ob):
    return str (date_ob.year) + '-' + str (date_ob.month) + '-' + str (date_ob.day) + ' ' + str (date_ob.hour) + ':' + str (date_ob.minute)

def render_comment_create (rest_vars):
    require_logged_in ()
    slug = rest_vars.page_slug
    page = load_page (slug)
    if (not request.vars.has_key ('body')) or (len (request.vars.get ('body')) == 0):
        redirect (URL (r = request, args = [slug, 'view']))
    #w = db.plugin_wiki_page
    #page = w(slug = slug)
    #db.plugin_wiki_comment.insert(page_id = page.id, body = request.vars.get ('body'))
    #db (db.plugin_wiki_page.slug == slug).update (comments = (page.comments + 1))
    import datetime
    mongo.blog.update ({'slug': slug}, {'$push': {'comments': {
                    'date': datetime.datetime.now (),
                    'owner': auth.user.id,
                    'body': request.vars.get ('body'),                    
                    '_id': ObjectId (),
                    }}})
    redirect (URL (r = request, args = [slug, 'view']))

def render_comment_delete (rest_vars):
    slug = rest_vars.page_slug
    if not slug:
        raise HTTP (400)
    lookup_id = require_hex (rest_vars.comment_id)
    comment = MongoWrapper (mongo.blog.find_one ({'slug': slug, 'comments._id': ObjectId (lookup_id)}))
    require_page_authorized (comment)
    mongo.blog.update ({'slug': slug}, {
            '$pull': {
                'comments': {
                    '_id': ObjectId (lookup_id),
                    }
                }
            })
    redirect (URL (r = request, args = [slug, 'view']))

def render_publish (rest_vars):
    page = load_page (rest_vars.page_slug)
    require_page_authorized (page)

    mongo.blog.update ({'slug': page.slug}, {'$set': {'public': True}})
    redirect (URL (r = request))

def render_unpublish (rest_vars):
    page = load_page (rest_vars.page_slug)
    require_page_authorized (page)

    mongo.blog.update ({'slug': page.slug}, {'$set': {'public': False}})
    redirect (URL (r = request))

def render_delete_confirm (rest_vars):
    response.view = 'wiki/delete_confirm.html'    
    return {'slug': rest_vars.page_slug}

def render_delete (rest_vars):
    page = load_page (rest_vars.page_slug)
    require_page_authorized (page)

    mongo.blog.remove ({'slug': page.slug})
    redirect (URL (r = request))

def render_categories (rest_vars):
    require_role (editor_role)
    response.view = 'wiki/categories.html'    
    if request.vars.has_key ('name'):
        vars = request.vars
        cat = {
            'name': vars.name,
            'blog': vars.blog == 'on',
            'case': vars.case == 'on',
            'docs': vars.docs == 'on',
            'tutorials': vars.tutorials == 'on',
            }
        if len (vars.name) == 0:
            response.flash = "Category name must be defined"
        elif not vars.has_key ('_id'):
            if mongo.categories.find ({'name': vars.name}).count ():
                response.flash = "Category %s is already defined" % vars.name
            else:
                mongo.categories.insert (cat)
        else:
            mongo.categories.update ({'_id': ObjectId (vars._id)}, {'$set': cat})
    results = MongoWrapper (mongo.categories.find ())
    return {'categories': results}
