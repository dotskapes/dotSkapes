from copy import deepcopy
from uuid import uuid4
import simplejson as json

def boolean (val):
    if isinstance (val, str):
        lower = val.lower ()
        if lower == 'false':
            return False
        elif lower == 'f':
            return False
        elif lower == 'true':
            return True
        elif lower == 't':
            return True
    elif isinstance (val, int):
        if val == 0:
            return False
        elif val == 1:
            return True
    elif isinstance (val, float):
        if val == 0.0:
            return False
        elif val == 1.0:
            return True
    else:
        if val is None:
            return False
    raise RuntimeError ('Cast to boolean failed: Could not convert ' +
                        str (val) + ' to a boolean')

def cond_assign (dst, src, key):
    if src.has_key (key):
        dst[key] = src[key]

class attr_dict (dict):
    def __init__ (self, **attr):
        dict.__init__ (self, **attr)

    def __getattr__ (self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def default (self, key, default):
        if self.has_key (key):
            return
        else:
            self[key] = default


class DM_List (list):
    def __init__ (self, *args):
        list.__init__ (self, *args)

    def first (self):
        if len (self) == 0:
            return None
        else:
            return self[0]

    def json (self):
        return json.dumps (map (lambda x: x.public (), self))


class DM_Entry (dict):
    def __init__ (self, model):
        if model is None:
            raise HTTP (400, "Attempt to create entry without a model")
        self.model = model
        dict.__init__ (self)

    def __getattr__ (self, key):
        return dict.__getitem__ (self, key)

    def public (self):
        publicValues = {}
        for key in self.model.public ():
            publicValues[key.name] = self[key.name]
        publicValues['id'] = self['id']
        return attr_dict (**publicValues)

    def json (self):
        return json.dumps (self.public ())


class DM_Field (attr_dict):
    def __init__ (self, name, field_type, **attr):
        self.name = name
        self.type = field_type
        self.lookup_id = 'f_' + self.name
        attr_dict.__init__ (self, **attr)

    #def __deepcopy__ (self, memo):
    #    pass

    def toField (self):
        if self.type == 'table':
            return Field (self.lookup_id, 'string', default = None)
        kw = {}
        cond_assign (kw, self, 'default')
        cond_assign (kw, self, 'required')
        return Field (self.lookup_id, self.type, **kw)

    def display (self):
        kw = {}
        cond_assign (kw, self, 'title')
        cond_assign (kw, self, 'visible')
        cond_assign (kw, self, 'text')
        if not kw.has_key ('text'):
            kw['text'] = self.name
        return kw


class DM_TableModel (dict):
    def __init__ (self, *fields, **kw):
        if kw.has_key ('name'):
            self.name = kw['name']
        else:
            self.name = None
        values = []
        self.publicList = []
        for item in fields:
            values.append ((item.name, item))
            if not item.private and not item.protected:
                self.publicList.append (item)
        dict.__init__ (self, values) 
        
    def map_key (self, key):
        return 'f_' + key

    def __deepcopy__ (self, memo):
        return DM_TableModel (*self, name = self.name)

    def __iter__ (self):
        return iter (self.values ())

    def append (self, field):
        self[field.name] = field

    def toFields (self):
        return map (lambda item: item.toField (), self.values ())

    def public (self):
        return self.publicList

'''class DM_TableFactory:
    def __init__ (self, name = None, writeback = None, entry = None, col = None):
        self.name = name
        self.writeback = writeback
        self.entry = entry
        self.col = col
        self.model = False

    def exists (self):
        return False'''

      
class DM_Table:
    def __init__ (self, name = None, model = None, writeback = None):
        self.name = name
        self.writeback = writeback
        self.ex = (name in db.tables)
        self.model = model

    def exists (self):
        return self.ex

    def create (self, model = None):
        if model:
            self.model = model
        if self.ex:
            return
        if not self.model:
            raise HTTP (400, 'Attempt access abstract table')
        if not self.name:
            self.name = 't' + uuid4 ().hex
        db.define_table (self.name, *(self.model.toFields ()))
        if self.writeback:
            db (db[self.writeback[0]].id == self.writeback[1]).update (**{self.writeback[2]: self.name})
        self.ex = True

    def all (self):
        if not self.ex:
            self.create (self.model)
        entries = db (db[self.name].id >= 0).select ()
        result = DM_List ()
        for e in entries:
            result.append (self.__load (e))
        return result

    def multi_get (self, entry_ids):
        if not self.ex:
            self.create (self.model)
        query = None
        for key in entry_ids:
            next = (db[self.name].id == key)
            if query:
                query = query | next
            else:
                query = next
        if query:
            entries = db (query).select ()
        else:
            entries = []
        result = DM_List ()
        for e in entries:
            result.append (self.__load (e))
        return result

    def get (self, entry_id):
        if not self.ex:
            self.create (self.model)
        entry = db (db[self.name].id == entry_id).select ().first ()
        if not entry:
            raise HTTP (400, 'Record Not Found')
        return self.__load (entry)

    def query (self, **kw):
        query = self.__make_query (kw)
        entries = db (query).select ()
        result = DM_List ()
        for e in entries:
            result.append (self.__load (e))
        return result

    def delete (self, **kw):
        query = self.__make_query (kw)
        db (query).delete ()

    def insert (self, **values):
        if not self.ex:
            self.create (self.model)
        data = {}
        for item in self.model:
            if values.has_key (item.name):
                if item.type == 'table':
                    data[self.model.map_key (item.name)] = values[item.name].name
                else:
                    data[self.model.map_key (item.name)] = values[item.name]
        return db[self.name].insert (**data)

    def update (self, entry_id, **values):
        if not self.ex:
            self.create (self.model)
        data = {}
        for v in values:
            data[self.model.map_key (v)] = values[v]
        db (db[self.name].id == entry_id).update (**data)

    def __load (self, entry):
        val = DM_Entry (self.model)
        for field in self.model:
            key = field.name
            lookup_id = self.model.map_key (key)
            if field.type == 'table':
        #for key, value in entry.iteritems ():
            #if self.model[key].type == 'table':
                if entry[lookup_id] is None:
                    val[key] = DM_Table (writeback = (self.name, entry['id'], lookup_id), model = field.model)
                else:
                    if field.model:
                        val[key] = DM_Table (name = entry[lookup_id], model = field.model)
                    else:
                        val[key] = DM_Table (name = entry[lookup_id])
            else:
                val[key] = entry[lookup_id]
        val['id'] = entry['id']
        return val

    def __make_query (self, kw):
        if not self.ex:
            self.create (self.model)
        query = None
        for key, value in kw.iteritems ():
            next = (db[self.name][self.model.map_key (key)] == value)
            if query:
                query = query & next
            else:
                query = next
        return query


class DataManager:
    def __init__ (self):
        self.root = DM_Table ('datatypes', root_table)
        self.__checker = set ()
        self.models = {}

    def define_datatype (self, datatype, model):
        if datatype in self.__checker:
            raise HTTP (500, 'Attempt to redefine datatype')
        self.__checker.add (datatype)
        self.models[datatype] = deepcopy (model)
        self.models[datatype].append (DM_Field ('owner', 'integer', private = True, default = -1))
        self.models[datatype].append (DM_Field ('public', 'boolean', private = True, default = False))
        entry = self.root.query (datatype = datatype).first ()
        if not entry:
            id = self.root.insert (datatype = datatype) 
            lookup = self.root.get (id)
            lookup.data.create (self.models[datatype])
            lookup.user.create ()
            lookup.kw.create ()

    def insert (self, datatype, **kw):
        user_id = require_logged_in ()
        kw['owner'] = user_id
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        id = lookup.data.insert (**kw)
        return id

    def update (self, datatype, entry_id, **kw):
        user_id = require_logged_in ()
        entry = dm.get (datatype, entry_id)
        if entry.owner != user_id:
             raise HTTP (400, 'Permission Denied to edit data')
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        id = lookup.data.update (entry_id, **kw)

    def global_load (self, datatype, keywords = None):
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        if not keywords:
            return lookup.data.query (public = True)
        else:
            keys = set ()
            for kw in keywords:
                key_table = lookup.kw.query (name = kw).first ()
                if not key_table:
                    continue
                else:
                    current_keys = key_table.ref.all ()
                    for k in current_keys:
                        keys.add (k.ref)
            return lookup.data.multi_get (keys)

    def local_load (self, datatype, keywords = None):
        user_id = require_logged_in ()
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        ref_table = lookup.user.query (user = user_id).first ()
        if not ref_table:
            id = lookup.user.insert (user = user_id)
            ref_table = lookup.user.get (id)
        user_table = ref_table.ref
        result = user_table.all ()
        loadList = []
        for r in result:
            loadList.append (r.ref)
        return lookup.data.multi_get (loadList)

    def get (self, datatype, object_id):
        user_id = require_logged_in ()
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        result = lookup.data.get (object_id)
        if user_id != result.owner and not result.public:
            raise HTTP (400, "Attempt to access private data")
        return result
    
    def owner (self, datatype, object_id, user_id):
        pass

    def public (self, datatype, object_id, pub_status):
        user_id = require_logged_in ()
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        data = lookup.data.get (object_id)
        if user_id != data.owner:
            raise HTTP (400, "Permission denied to change permissions of resource")
        lookup.data.update (object_id, public = pub_status)

    def link (self, datatype, object_id):
        user_id = require_logged_in ()
        data = dm.get (datatype, object_id)
        if user_id != data.owner and not data.public:
            raise HTTP (400, "Permission denied to link resource")
        user_table = self.__traverse_to_user_table (datatype)
        user_table.insert (ref = object_id)

    def unlink (self, datatype, object_id):
        user_table = self.__traverse_to_user_table (datatype)
        user_table.delete (ref = object_id)

    def keywords (self, datatype, object_id, keywords):
        lookup = self.root.query (datatype = datatype).first ()
        for kw in keywords:
            key_table = lookup.kw.query (name = kw).first ()
            if not key_table:
                id = lookup.kw.insert (name = kw)
                key_table = lookup.kw.get (id)
            key_list = key_table.ref
            key_list.insert (ref = object_id)

    def dup (self, datatype, alt_datatype):
        if alt_datatype in self.__checker:
            raise HTTP (500, 'Attempt to redefine datatype')
        self.__checker.add (alt_datatype)
        self.models[alt_datatype] = deepcopy (self.models[datatype])
        #raise HTTP (400, str (self.models[alt_datatype]))
        entry = self.root.query (datatype = alt_datatype).first ()
        if not entry:
            lookup = self.root.query (datatype = datatype).first ()
            if not lookup:
                raise HTTP (400, 'Datatype not defined')
            id = self.root.insert (datatype = alt_datatype, data = lookup.data, kw = lookup.kw)
            lookup = self.root.get (id)
            lookup.user.create ()

    def get_types (self):
        return self.models

    def __traverse_to_user_table (self, datatype):
        user_id = require_logged_in ()
        lookup = self.root.query (datatype = datatype).first ()
        lookup.data.create (self.models[datatype])
        ref_table = lookup.user.query (user = user_id).first ()
        if not ref_table:
            id = lookup.user.insert (user = user_id)
            ref_table = lookup.user.get (id)
        user_table = ref_table.ref
        return user_table


user_data = DM_TableModel (DM_Field ('ref', 'integer'))

user_table = DM_TableModel (DM_Field ('user', 'integer'),
                            DM_Field ('ref', 'table', model = user_data),
)

keyword_list = DM_TableModel (DM_Field ('ref', 'integer'))

keyword_table = DM_TableModel (DM_Field ('name', 'string'),
                               DM_Field ('ref', 'table', model = keyword_list)
)

root_table = DM_TableModel (DM_Field ('datatype', 'string'),
                            DM_Field ('data', 'table'),
                            DM_Field ('user', 'table', model = user_table),
                            DM_Field ('kw', 'table', model = keyword_table),
)

dm = DataManager ()
