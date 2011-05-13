from uuid import uuid4

class attr_dict (dict):
    def __init__ (self, **attr):
        dict.__init__ (self, **attr)

    def __getattr__ (self, key):
        return self[key]

    def default (self, key, default):
        if self.has_key (key):
            return
        else:
            self[key] = default

class DM_Settings (attr_dict):
    def __init__ (self, **settings):
        attr_dict.__init__ (self, **settings)    
        self.default ('privilaged', False)


class DM_Field:
    def __init__ (self, field, manager_settings, display_settings):
        self.field = field
        if manager_settings is None:
            self.manager_settings = DM_Settings ()
        else:
            self.manager_settings = manager_settings
        if display_settings is None:
            self.display_settings = DisplaySettings ()
        else:
            self.display_settings = display_settings
        '''
        if kwargs.has_key ('privilaged') :
            self.privilaged = kwargs['privilaged']
            del kwargs['privilaged']
        else:    
            self.privilaged = False
        if kwargs.has_key ('text_field') :
            self.text_field = kwargs['text_field']
            del kwargs['text_field']
        else:    
            self.text_field = False
        self.name = name
        self.field_type = field_type
        self.kwargs = kwargs'''

    def name (self): 
        return self.field.name

    def is_privilaged (self):
        return self.manager_settings.privilaged

    def to_field (self):
        return self.field

class DM_List (list):
    def __init__ (self, fields = []):
        self.fields = fields
        list.__init__ (self)

    def json (self):
        import simplejson as json
        data_set = []
        for item in self:
            entry = {}
            for field in self.fields:
                if not field.manager_settings['privilaged']:
                    entry[field.field.name] = item[field.field.name]
            data_set.append (entry)
        return json.dumps ({'data': data_set})

class DM_Dict (dict):
    def __init__ (self, fields):
        self.fields = fields
        dict.__init__ (self)

    def json (self):
        import simplejson as json
        data_set = {}
        for field in self.fields:
            if not field.manager_settings['privilaged']:
                data_set[field.name] = self[field.name]
        return json.dumps (data_set)

class DataManager:
    def __init__ (self):
        self.__checker = set ()
        self.__fields = {}
        #self.privilaged = {}
        db.define_table ('datatypes',
                         Field ('name', 'string', required = True),  
                         Field ('data_table', 'string', default = None),
                         Field ('user_table', 'string', default = None),
                         Field ('key_table', 'string', default = None),
        )

    def __define_data_table (self, data_table, fields):
        if db.has_key (data_table):
            return
        db.define_table (data_table, 
                         Field ('owner', 'integer', default = -1),
                         Field ('public', 'boolean', default = False),
                         *map (lambda f: f.to_field (), fields))

    def __define_user_table (self, user_table):
        if db.has_key (user_table):
            return
        db.define_table (user_table, 
                         Field ('user_id', 'integer', required = True),
                         Field ('table_ref', 'string', default = None),
        )

    def __define_key_table (self, key_table):
        if db.has_key (key_table):
            return
        db.define_table (key_table, 
                         Field ('kw', 'string', required = True),
                         Field ('table_ref', 'string', required = True),
        )

    def __define_word_table (self, word_table):
        if db.has_key (word_table):
            return
        db.define_table (word_table, 
                         Field ('ref', 'integer', required = True),
        )

    def __define_sub_table (self, sub_table):
        if db.has_key (sub_table):
            return
        db.define_table (sub_table,
                         Field ('ref', 'integer', required = True),
        )
    
    def define_datatype (self, datatype, *fields):
        if datatype in self.__checker:
            raise HTTP (500, 'Internal Error')
        self.__fields[datatype] = fields
        #self.privilaged[datatype] = {}
        '''for f in fields:
            if not f.privilaged:
                self.privilaged[datatype][f.name] = f.privilaged'''
        self.__checker.add (datatype)
        result = db (db.datatypes.name == datatype).select ().first ()
        if not result:
            data_table = 't' + str (uuid4().hex)
            user_table = 't' + str (uuid4().hex)
            key_table  = 't' + str (uuid4().hex)
            db.datatypes.insert (name = datatype, data_table = data_table, user_table = user_table, key_table = key_table)
        else:
            data_table = result.data_table
            user_table = result.user_table
            key_table =  result.key_table
        self.__define_data_table (data_table, fields)
        self.__define_user_table (user_table)
        self.__define_key_table (key_table)
        #self.__fields[datatype] = set ()
        #for f in fields:
        #    self.__fields[datatype].add (f)

    def __get_lookup_tables (self, datatype):
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        if lookup_tables is None:
            raise HTTP (500, "Internal Error")
        return lookup_tables

    def __get_ref_table (self, user_id, lookup_table):
        user_table = db (db[lookup_table].user_id == user_id).select ().first ()
        if user_table is None:
            ref_table = 't' + str (uuid4().hex)
            db[lookup_table].insert (user_id = user_id, table_ref = ref_table)
        else:
            ref_table = user_table.table_ref
        self.__define_sub_table (ref_table)
        return ref_table

    def __link_ref (self, ref_table, ref_id):
        key = db[ref_table].insert (ref = ref_id)
        return key

    def __gloabl_id (self, datatype, user_id, id):
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        user_table = db (db[lookup_tables.user_table].user_id == user_id).select ().first ()
        if user_table is None:
            raise HTTP (400, "Bad Request")
        ref_table = user_table.table_ref
        self.__define_sub_table (ref_table)
        data = db (db[ref_table].id == id).select ().first ()
        if data is None:
            raise HTTP (400, "Bad Request")
        else:
            return data.ref

    def get_types (self):
        return self.__fields.keys ()

    def get_fields (self, datatype):
        return self.__fields[datatype]

    def get (self, datatype, data_id):
        user_id = require_logged_in ()
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        user_table = db (db[lookup_tables.user_table].user_id == user_id).select ().first ()
        if user_table is None:
            raise HTTP (400, "Bad Request")
        ref_table = user_table.table_ref
        self.__define_sub_table (ref_table)
        result = db (db[ref_table].id == data_id).select ().first ()
        if result is None:
            raise HTTP (400, 'Bad Request')
        data = db (db[lookup_tables.data_table].id == result.ref).select ().first ()
        if data is None:
            raise HTTP (400, "Bad Request")
        item = DM_Dict (self.__fields[datatype])
        item.update (data.as_dict ())
        item['id'] = data_id
        return item

    def add_keyword (self, datatype, id, *args):
        user_id = require_logged_in ()
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        for kw in args:
            table_ref = db (db[lookup_tables.key_table].kw == kw).select ().first () 
            if table_ref is None:
                ref_table = 't' + str (uuid4().hex)
                db[lookup_tables.key_table].insert (kw = kw, table_ref = ref_table)
            else:
                ref_table = table_ref.table_ref
            self.__define_word_table (ref_table)
            db[ref_table].insert (ref = self.__gloabl_id (datatype, user_id, id))
        

    def load_keyworded (self, datatype, kw):
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        table = db (db[lookup_tables.key_table].kw == kw).select ().first () 
        if table is None:
            return DM_List ()
        else:
            ref_table = table.table_ref
            self.__define_word_table (ref_table)
            data = db ((db[lookup_tables.data_table].id == db[ref_table].ref) & (db[lookup_tables.data_table].public == True)).select ().as_list ()
            selection = DM_List (self.__fields[datatype])
            for entry in data:
                item = entry[lookup_tables.data_table]
                item['id'] = entry[ref_table]['id']
                selection.append (item)
            return selection

    def load_public (self, datatype):
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        data = db (db[lookup_tables.data_table].public == True).select ()
        selection = DM_List (self.__fields[datatype])
        selection += data.as_list ()
        return selection

    def load (self, datatype):
        lookup_tables = db (db.datatypes.name == datatype).select ().first ()
        user_id = require_logged_in ()
        user_table = db (db[lookup_tables.user_table].user_id == user_id).select ().first ()
        if user_table is None:
            return DM_List ()
        ref_table = user_table.table_ref
        self.__define_sub_table (ref_table)
        data = db (db[lookup_tables.data_table].id == db[ref_table].ref).select ().as_list ()
        selection = DM_List (self.__fields[datatype])
        for entry in data:
            item = entry[lookup_tables.data_table]
            item['id'] = entry[ref_table]['id']
            selection.append (item)
        return selection

    def insert (self, datatype, **kwargs):
        kwargs['owner'] = require_logged_in ()
        lookup_tables = self.__get_lookup_tables (datatype)
        key = db[lookup_tables.data_table].insert (**kwargs)
        ref_table = self.__get_ref_table (kwargs['owner'], lookup_tables.user_table)
        user_key = self.__link_ref (ref_table, key)
        return user_key

    def link (self, user_id, datatype, data_id):
        lookup_tables = self.__get_lookup_tables (datatype)
        entry = db (db[lookup_tables.data_table].id == data_id).select ().first ()
        if entry is None:
            raise HTTP (400, "Bad Request")
        if not entry.public and entry.owner != user_id:
            raise HTTP (401, "Permission Denied")
        ref_table = self.__get_ref_table (user_id, lookup_tables.user_table)
        user_key = self.__link_ref (ref_table, data_id)
        return user_key        


dm = DataManager ()

'''def ln (self, user_id, ref):
        pass

    def retrieve (self, name, id):
        pass

    def insert (self, name, **kwargs):
        pass

    def edit (self, name, id, **kwargs):
        pass'''

            
'''db.define_table ('userdata',
                 Field ('user_id', 'integer', required = True),
                 Field ('maps', 'string', default = None),
                 Field ('dev_tools', 'string', default = None),
                 Field ('pub_tools', 'string', default = None),
                 Field ('results', 'string', default = None),
                 Field ('analyses', 'string', default = None),
)'''

'''def define_sub_table (table_name):
    db.define_table (table_name,
                     Field ('data', 'string', required = True),
    )

def load_data (user_id, col):
    result = db (db.userdata.user_id == user_id).select ()[0][col]
    if not result:
        return []
    define_sub_table (result)
    data = db (db[result].id >= 0).select ()
    selection = []
    for d in data:
        selection.append (d.data)
    return selection

def append_data (user_id, col, data):
    result = db (db.userdata.user_id == user_id).select ()[0][col]
    if not result:
        table_name = 't' + str (uuid4().hex)
        db (db.userdata.user_id == user_id).update (**{col: table_name})
    else:
        table_name = result
    define_sub_table (table_name)
    key = db[table_name].insert (data = data)
    return key
'''
