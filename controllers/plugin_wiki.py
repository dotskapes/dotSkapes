# This file was developed by Massimo Di Pierro
# It is released under BSD, MIT and GPL2 licenses

##########################################################
# code to handle wiki pages
##########################################################


def index():
    from re import finditer
    w = db.plugin_wiki_page
    if check_role (editor_role):
        query = w.id > 0
    elif check_role (writer_role):
        query = (w.is_public == True) | (w.created_by == auth.user.id)
    else:
        query = w.is_public == True
    if request.vars.has_key ('search'):
        term = request.vars.get ('search')
        query = query & (w.body.contains (term) | w.title.contains (term))
    pages = db(query).select(orderby=~w.created_on)

    if request.vars.has_key ('start'):
        start = require_int (request.vars.get ('start'))
    else:
        start = 0

    if request.vars.has_key ('max'):
        max_ret = require_int (request.vars.get ('max'))
    else:
        max_ret = 10

    first = (start + max_ret >= len (pages))
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
        #if len (strings):
        #    return str (strings)
        strings.append (p.body[start:])
        
        #'(?=#)#{0, 3}/s[^\n]*\n)'
        #words = p.body.split (' ')
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
        p.cats = load_categories (p)
        
    #if plugin_wiki_editor:
    #    form=SQLFORM.factory(Field('slug',requires=db.plugin_wiki_page.slug.requires),
    #                         Field('from_template',requires=IS_EMPTY_OR(IS_IN_DB(db,db.plugin_wiki_page.slug))))
    #    if form.accepts(request.vars):
    #       redirect(URL(r=request,f='page',args=form.vars.slug,vars=dict(template=request.vars.from_template or '')))
    #else:
    #    form=''
    return dict(pages = pages, first = first, last = last, older = older, newer = newer)

def page():
    """
    shows a page
    """
    slug = request.args(0)
    if not slug:
        raise HTTP (400)
    w = db.plugin_wiki_page
    page = w(slug = slug)
    if not page.is_public:
        require_page_authorized (page)
    comments = db (db.plugin_wiki_comment.page_id == page.id).select ()
    for c in comments: 
        c.body = plugin_wiki.render (c.body)
    return dict(page=page,slug=slug, comments = comments)
    '''if not auth.user and (not page or not page.is_public or not page.is_active):
        redirect(URL(r=request,c='default',f='user',args='login'))
    elif not plugin_wiki_editor and (not page or not page.is_public or not page.is_active):
        raise HTTP(404)
    elif page and page.role and not auth.has_membership(page.role):    
        raise HTTP(404)
    if request.extension=='load':
        return plugin_wiki.render(page.body)
    if request.extension=='html':         
        return dict(page=page,slug=slug, comments = comments)
    return MARKMIN(page.body,extra={'widget':(lambda code:''),
                                    'template':(lambda template:'')})'''

def post_comment():
    require_logged_in ()
    slug = request.args(0)
    if not slug:
        raise HTTP (400)
    if (not request.vars.has_key ('body')) or (len (request.vars.get ('body')) == 0):
        redirect (URL (r = request, f = 'page.html', args = [slug]))
    w = db.plugin_wiki_page
    page = w(slug = slug)
    db.plugin_wiki_comment.insert(page_id = page.id, body = request.vars.get ('body'))
    db (db.plugin_wiki_page.slug == slug).update (comments = (page.comments + 1))
    redirect (URL (r = request, f = 'page.html', args = [slug]))

def delete_comment():
    slug = request.args(0)
    if not slug:
        raise HTTP (400)
    lookup_id = require_int (request.vars.get ('id'))
    comment = db (db.plugin_wiki_comment.id == lookup_id).select ().first ()
    comment.delete_record ()
    w = db.plugin_wiki_page
    page = w(slug = slug)
    db (db.plugin_wiki_page.slug == slug).update (comments = (page.comments - 1))
    redirect (URL (r = request, f = 'page.html', args = [slug]))
    

def page_archive():
    """
    shows and old version of a page
    """
    id = request.args(0)
    h = db.plugin_wiki_page_archive
    page = h(id)
    if not page or (not plugin_wiki_editor and (not page.is_public or not page.is_active)):
        raise HTTP(404)
    elif page and page.role and not auth.has_membership(page.role):
        raise HTTP(404)
    if request.extension!='html': return page.body
    return dict(page=page)

def page_create():
    '''require_role (writer_role)
    w = db.plugin_wiki_page

    def process_req (f):
        redirect (URL (r=request,f='page_edit',args=f.vars.slug))
    
    form = crud.create (w,
                        onaccept = process_req)
                       #next=URL(r=request,f='page_edit',args='[id]'))
    return {'form': form}'''
    require_role (writer_role)
    form = FORM ('', LABEL ('URL: '), INPUT (_name = 'page_title', requires=(IS_SLUG(), IS_NOT_IN_DB(db,'plugin_wiki_page.slug'))))
    if form.accepts (request, session):
        slug = request.vars.get ('page_title')
        w = db.plugin_wiki_page
        page = w.insert(slug=slug, 
                        title = '',
                        comments = 0,
                        is_active = True,
                        is_public = False,
                        created_by = auth.user.id,
                        body=request.vars.template and w(slug=request.vars.template).body or '')
        redirect (URL (r = request, f = 'page_edit', args = [slug], vars = {'create': True}))
    return {'form': form}

def page_edit():
    """
    edit a page
    """
    slug = request.args(0)
    if not slug:
        raise HTTP (400)
    w = db.plugin_wiki_page
    page = w(slug = slug)
    require_page_authorized (page)

    if request.vars.get ('create'):
        create = True
    else:
        create = False
        
    if request.vars.has_key ('slug'):
        new_slug = request.vars.get ('slug')
        if slug != new_slug:
            if (len (new_slug) == 0) or (db (w.slug == new_slug).count () > 0):
                response.flash = 'URL Already Exists'
                return dict (page = request.vars, create = create)
        vars = request.vars
        db (w.slug == slug).update (slug = vars.slug, title = vars.title, is_public = vars.is_public, body = vars.body)
        redirect (URL (r = request, f = 'index.html'))
    else:
        return dict (page = page, create = create)


def page_publish_toggle():
    slug = request.args(0)
    if not slug:
        raise HTTP (400, "No page URL given")
    page = db (db.plugin_wiki_page.slug == slug).select ().first ()
    if not page:
        raise HTTP (404, "Page not found")

    require_page_authorized (page)
    page.update_record (is_public = (not page.is_public))
    redirect (URL (r = request, f = 'index.html'))

def page_delete():
    page = load_page (request.args(0))
    require_page_authorized (page)
    form = FORM (LABEL ('Confirm deletion of page ' + page.slug), BR (),
                 INPUT (_type='submit', _value = 'Delete'))
    if form.accepts (request, session):
        page.delete_record ()
        redirect (URL (r = request, f = 'index.html'))
    return {'form': form}

def category_add():
    page = load_page (request.args(0))
    require_page_authorized (page)
    cid = require_int (request.vars.get ('cid'))
    return str (db.plugin_wiki_page_categories.insert (pid = page.id, cid = cid))

def category_delete():
    page = load_page (request.args(0))
    require_page_authorized (page)
    cat_id = require_int (request.vars.get ('cid'))
    db ((db.plugin_wiki_page_categories.cid == cat_id) & (db.plugin_wiki_page_categories.pid == page.id)).delete ()

def categories_edit():
    require_role (editor_role)
    if request.vars.has_key ('category'):
        c = request.vars.get ('category')
        if len (c) == 0:
            pass
        elif db (db.plugin_wiki_categories.category == c).count () > 0:
            response.flash = 'Category is already defined'
        else:
            db.plugin_wiki_categories.insert (category = c)
    results = db (db.plugin_wiki_categories).select ()
    return {'categories': results}

def page_history():
    """
    show page changelog
    """
    slug = request.args(0) or 'index'
    w = db.plugin_wiki_page
    h = db.plugin_wiki_page_archive
    page = w(slug=slug)
    history = db(h.current_record==page.id).select(orderby=~h.modified_on)
    return dict(page=page, history=history)


##########################################################
# ajax callbacks
##########################################################
@auth.requires_login()
def attachments():
    """
    allows to edit page attachments
    """
    a=db.plugin_wiki_attachment
    a.tablename.default=tablename=request.args(0)
    a.record_id.default=record_id=request.args(1)
    #if request.args(2): a.filename.writable=False
    form=crud.update(a,request.args(2),
                     next=URL(r=request,args=request.args[:2]))
    if request.vars.list_all:
        query = a.id>0
    else:
        query = (a.tablename==tablename)&(a.record_id==record_id)
    rows=db(query).select(orderby=a.name)
    return dict(form=form,rows=rows)

def attachment():
    """
    displays an attachments
    """
    short=request.args(0)
    if plugin_wiki_authorize_attachments and \
            not short in session.plugin_wiki_attachments:
        raise HTTP(400)
    a=db.plugin_wiki_attachment
    record=a(short.split('.')[0])
    if not record: raise HTTP(400)
    request.args[0]=record.filename
    return response.download(request,db)

def comment():
    """
    post a comment
    """
    tablename, record_id = request.args(0), request.args(1)
    table=db.plugin_wiki_comment
    if record_id=='None': record_id=0
    table.tablename.default=tablename
    table.record_id.default=record_id
    if auth.user:
        form = crud.create(table)
    else:
        form = A(T('login to comment'),_href=auth.settings.login_url)
    comments=db(table.tablename==tablename)\
        (table.record_id==record_id).select()
    return dict(form = form,comments=comments)

#@auth.requires_login()
def jqgrid():
    """
    jqgrid callback retrieves records
    http://trirand.com/blog/jqgrid/server.php?q=1&_search=false&nd=1267835445772&rows=10&page=1&sidx=amount&sord=asc&searchField=&searchString=&searchOper=
    """
    from gluon.serializers import json
    import cgi
    hash_vars = 'tablename|columns|fieldname|fieldvalue|user'.split('|')
    if not URL.verify(request,hmac_key=auth.settings.hmac_key,
                      hash_vars=hash_vars,salt=auth.user_id):
        raise HTTP(404)    
    tablename = request.vars.tablename or error()
    columns = (request.vars.columns or error()).split(',')
    rows=int(request.vars.rows or 25)
    page=int(request.vars.page or 0)
    sidx=request.vars.sidx or 'id'
    sord=request.vars.sord or 'asc'
    searchField=request.vars.searchField
    searchString=request.vars.searchString
    searchOper={'eq':lambda a,b: a==b,
                'nq':lambda a,b: a!=b,
                'gt':lambda a,b: a>b,
                'ge':lambda a,b: a>=b,
                'lt':lambda a,b: a<b,
                'le':lambda a,b: a<=b,
                'bw':lambda a,b: a.like(b+'%'),
                'bn':lambda a,b: ~a.like(b+'%'),
                'ew':lambda a,b: a.like('%'+b),
                'en':lambda a,b: ~a.like('%'+b),
                'cn':lambda a,b: a.like('%'+b+'%'),
                'nc':lambda a,b: ~a.like('%'+b+'%'),
                'in':lambda a,b: a.belongs(b.split()),
                'ni':lambda a,b: ~a.belongs(b.split())}\
                [request.vars.searchOper or 'eq']
    table=db[tablename]
    if request.vars.fieldname:
        names = request.vars.fieldname.split('|')
        values = request.vars.fieldvalue.split('|')
        query = reduce(lambda a,b:a&b,
                       [table[names[i]]==values[i] for i in range(len(names))])
    else:
        query = table.id>0
    dbset = table._db(query)
    if searchField: dbset=dbset(searchOper(table[searchField],searchString))
    orderby = table[sidx]
    if sord=='desc': orderby=~orderby
    limitby=(rows*(page-1),rows*page)
    fields = [table[f] for f in columns]
    records = dbset.select(orderby=orderby,limitby=limitby,*fields)
    nrecords = dbset.count()
    items = {}
    items['page']=page
    items['total']=int((nrecords+(rows-1))/rows)
    items['records']=nrecords
    readable_fields=[f.name for f in fields if f.readable]
    def f(value,fieldname):
        r = table[fieldname].represent
        if r: value=r(value)
        try: return value.xml()
        except: return cgi.escape(str(value))
    items['rows']=[{'id':r.id,'cell':[f(r[x],x) for x in readable_fields]} \
                       for r in records]
    return json(items)


def tags():
    import re
    db_tag = db.plugin_wiki_tag
    db_link = db.plugin_wiki_link
    table_name=request.args(0)
    record_id=request.args(1)
    if not auth.user_id:
        return ''
    form = SQLFORM.factory(Field('tag_name',requires=IS_SLUG()))
    if request.vars.tag_name:
        for item in request.vars.tag_name.split(','):
            tag_name = re.compile('\s+').sub(' ',item).strip()
            tag_exists = tag = db(db_tag.name==tag_name).select().first()
            if not tag_exists:
                tag = db_tag.insert(name=tag_name, links=1)
            link = db(db_link.tag==tag.id)\
                (db_link.table_name==table_name)\
                (db_link.record_id==record_id).select().first()
            if not link:
                db_link.insert(tag=tag.id,
                               table_name=table_name,record_id=record_id)
                if tag_exists:
                    tag.update_record(links=tag.links+1)
    for key in request.vars:
        if key[:6]=='delete':
            link_id=key[6:]
            link=db_link[link_id]
            del db_link[link_id]
            db_tag[link.tag] = dict(links=db_tag[link.tag].links-1)
    links = db(db_link.table_name==table_name)\
              (db_link.record_id==record_id).select()\
              .sort(lambda row: row.tag.name.upper())
    return dict(links=links, form=form)

def cloud():
    tags = db(db.plugin_wiki_tag.links>0).select(limitby=(0,20))
    if tags:
        mc = max([tag.links for tag in tags])
    return DIV(_class='plugin_wiki_tag_cloud',*[SPAN(A(tag.name,_href=URL(r=request,c='plugin_wiki',f='page',args=('tag',tag.id))),_style='font-size:%sem' % (0.8+1.0*tag.links/mc)) for tag in tags])

@auth.requires(plugin_wiki_editor)
def widget_builder():
    """
    >> inspect.getargspec(PluginWikiWidgets.tags)
    (['table', 'record_id'], None, None, ('None', None))
    >>> dir(PluginWikiWidgets)
    """
    import inspect
    name=request.vars.name
    if plugin_wiki_widgets=='all':
        widgets = ['']+[item for item in dir(PluginWikiWidgets) if item[0]!='_']
    else:
        widgets = plugin_wiki_widgets
    form=FORM(LABEL('Widget Name: '), SELECT(_name='name',value=name,
                     _onchange="jQuery(this).parent().submit()",*widgets))
    widget_code=''
    if name in widgets: 
        a,b,c,d=inspect.getargspec(getattr(PluginWikiWidgets,name))
        a,d=a or [],d or []
        null = lambda:None
        d=[null]*(len(a)-len(d))+[x for x in d]
        ESC='x'
        fields = [Field(ESC+a[i],label=a[i],default=d[i]!=null and d[i] or '',
                        requires=(d[i]==null) and IS_NOT_EMPTY() or None,
                        comment=(d[i]==null) and 'required' or '') \
                      for i in range(len(a))]
        form_widget=SQLFORM.factory(hidden=dict(name=name),*fields)
        doc = getattr(PluginWikiWidgets,name).func_doc or ''
        if form_widget.accepts(request.vars):
            keys=['name: %s' % request.vars.name]
            for name in a:
                if request.vars[ESC+name]:
                    keys.append(name+': %s' % request.vars[ESC+name])
            widget_code=CODE('``\n%s\n``:widget' % '\n'.join(keys))
    else:
        doc=''
        form_widget=''
    return dict(form=form,form_widget=form_widget,doc=doc,
                widget_code=widget_code)


def star_rate():
    N=5 #max no of stars (if you use split stars you'll get a rating out of 10)
    pm = db.plugin_wiki_rating
    pa = db.plugin_wiki_rating_aux
    tablename = request.args(0)
    record_id = request.args(1)
    rating = abs(float(request.vars.rating or 0)) 
    
    try:
        db[tablename] #if there's no such table. Salute.
        if rating>N or rating<0: raise Exception #similar if rating is simulated.
        if not db[tablename][record_id]: raise Exception #also if there's no specified record in table
        if not auth.user_id: raise Exception #user has to login to rate
    except:
        return ''
        
    master = db(pm.tablename==tablename)(pm.record_id==record_id).select().first()    
    
    if master:
        master_rating, master_counter = master.rating, master.counter
    else:
        master_rating, master_counter = 0, 0
        master=pm.insert(tablename=tablename,record_id=record_id,rating=master_rating,counter=master_counter)        
        
    record = db(pa.master==master)(pa.created_by==auth.user_id).select().first()
        
    if rating:
        if not record:
           record = pa.insert(master=master,rating=rating,created_by=auth.user_id)
           master_rating = (master_rating*master_counter + rating)/(master_counter+1)
           master_counter = master_counter + 1
        else:
           master_counter = master_counter
           master_rating = (master_rating*master_counter - record.rating + rating)/master_counter
           record.update_record(rating=rating)
        master.update_record(rating=master_rating, counter=master_counter)        
    try:  
        db[tablename][record_id]['rating']
    except:
        return ''
    else:
        db[tablename][record_id].update_record(rating=master_rating)
        
    return ''
    
