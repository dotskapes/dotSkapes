import pymongo
from pymongo.objectid import ObjectId
import pymongo.cursor

class MongoWrapper:
    def __init__ (self, cursor, model = None):
        if model:
            if not cursor['public']:
                if not auth.user.id == cursor['owner']:
                    raise HTTP (401)
        self.__dict__['cursor'] = cursor
        self.__dict__['model'] = model

    def __getattr__ (self, key):
        try:
            return getattr (self.cursor, key)
        except AttributeError:
            try:
                val = self.cursor[unicode (key)]
                if (type (val) == list) or (type (val) == dict):
                    return MongoWrapper (self.cursor[unicode (key)], self.model)
                else:
                    return val
            except KeyError:
                return None

    def __nonzero__ (self):
        if self.cursor is None:
            return False
        return len (self.cursor) != 0

    def __iter__ (self):
        return MongoWrapperIter (self.cursor, self.model)

    def public (self):
        result = {}
        result['id'] = str (self.cursor['_id'])
        for key in self.model.public ():
            if self.cursor.has_key (key.name):
                result[key.name] = self.cursor[key.name]
            else:
                result[key.name] = None
        return result

    def json (self):
        return json.dumps (self.public ())


class MongoCursorWrapper:
    def __init__ (self, cursor, model = None):
        self.__cursor = cursor
        self.model = model

    def first (self):
        if self.__cursor.count () > 0:
            return self[0]
        else:
            return None

    def __getattr__ (self, key):
        return getattr (self.__cursor, key)

    def __getitem__ (self, index):
        record = self.__cursor[index]
        if self.model:
            if not record['public']:
                if not auth.user.id == record['owner']:
                    raise HTTP (401)
        return MongoWrapper (record, self.model)

    def json (self):
        result = []
        for item in self:
            result.append (item.public ())
        return json.dumps (result)

    def __len__ (self):
        return self.__cursor.count ()
    
    def __iter__ (self):
        return MongoWrapperIter (self.__cursor, self.model)

class MongoWrapperIter:
    def __init__ (self, cursor, model):
        self.__cursor = iter (cursor)
        self.model = model

    def __iter__ (self):
        return self

    def next (self):
        val = self.__cursor.next ()
        if (type (val) == list) or (type (val) == dict):
            return MongoWrapper (val, self.model)
        else:
            return val

class MongoCollectionWrapper:
    def __init__ (self, name, model):
        self.name = name
        self.model = model
    
    def authorized (self, record):
        if not record['public']:
            if not auth.user.id == record['owner']:
                raise RuntimeError ()
            
    def __getattr__ (self, key):
        def action (*args, **kw):
            data = getattr (mongo[self.name], key) (*args, **kw)
            if type (data) == pymongo.cursor.Cursor:
                return MongoCursorWrapper (data, self.model)
            elif type (data) == dict:
                return MongoWrapper (data, self.model)
            else:
                return data
        return action


class DataManager:
    def __init__ (self):
        self.collections = {}
        self.models = {}

    def user (self):
        user = mongo.users.find_one ({'user_id': auth.user.id})
        if not user:
            user = {'user_id': auth.user.id}
            mongo.users.insert (user)
            #print 'creating user'
        return user

    def define_datatype (self, datatype, model):
        self.models[datatype] = model
        self.collections[datatype] = MongoCollectionWrapper (datatype, model)

    def insert (self, datatype, **kw):
        kw['owner'] = auth.user.id
        if not kw.has_key ('tags'):
            kw['tags'] = []
        if not kw.has_key ('public'):
            kw['public'] = False
        return self.collections[datatype].insert (kw)
    
    def count (self, datatype):
        return self.collections[datatype].count ()

    def update (self, datatype, entry_id, **kw):
        self.collections[datatype].update ({'_id': ObjectId (entry_id)}, {'$set': kw})

    def global_load (self, datatype, kw = None):
        if not kw:
            data = self.collections[datatype].find ()
        else:
            kw_regex = kw[0]
            data = self.collections[datatype].find ({'name': {'$regex': kw_regex, '$options': 'i'}})
        return data

    def local_load (self, datatype, keywords = None):
        user = dm.user ()
        if not user.has_key (datatype):
            user[datatype] = []
            mongo.users.update ({'_id': user['_id']}, {'$set': {datatype: []}})
        ids = user[datatype]
        #data = mongo[datatype].find ({'_id': {'$in': ids}})
        data = self.collections[datatype].find ({'_id': {'$in': map (lambda x: ObjectId (x), ids)}})
        return data

    def load_keyworded (self, datatype, kw):
        return self.collections[datatype].find ({'tags': {'$in': kw}})

    def get (self, datatype, object_id):
        return self.collections[datatype].find_one ({'_id': ObjectId (object_id)})

    def query (self, datatype, **query):
        return self.collections[datatype].find (query)

    def owner (self, datatype, object_id):
        data = self.collections[datatype].find_one ({'_id': ObjectId (object_id)})

    def public (self, datatype, object_id, pub_status):
        self.collections[datatype].update ({'_id': ObjectId (object_id)}, {'$set': {'public': pub_status}})

    def link (self, datatype, object_id):
        dm.user ()
        mongo.users.update ({'user_id': auth.user.id}, {'$push': {datatype: ObjectId (object_id)}})
        #print dm.user ()

    def unlink (self, datatype, object_id):
        mongo.users.update ({'user_id': auth.user.id}, {'$pull': {datatype: ObjectId (object_id)}})

    def delete (self, datatype, **kw):
        self.collections[datatype].remove (kw)

    def dup (self, datatype, alt_datatype):
        self.models[alt_datatype] = self.models[datatype]
        self.collections[alt_datatype] = self.collections[datatype]

    def get_types (self):
        return self.models

    def tag (self, datatype, object_id, kw):
        self.collections[datatype].update ({'_id': ObjectId (object_id)}, {'$pushAll': {'tags': kw}})

    #def __ensure_user (self, user_id):
    #    if not mongo.users.find_one ({'user_id': user_id}):
    #        mongo.users.insert ({'user_id': user_id})

    #def __ensure_type (self, user_id, datatype):
    #    if not mongo.users.find_one ({'user_id': user_id, 
    #                                  datatype: {'$exists': true}
    #                                  }):
    #        mongo.users.update ({'user_id': user_id}, {datatype: []})

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

    def json (self):
        return json.dumps (self)

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

dm = DataManager ()
