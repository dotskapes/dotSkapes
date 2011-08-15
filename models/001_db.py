from gluon.tools import Crud

if deployment_settings.postgis.host:
    import psycopg2
    deployment_settings.postgis.connection = lambda: psycopg2.connect ('dbname=' + deployment_settings.postgis.database + ' user=' + deployment_settings.postgis.username + ' password=' + deployment_settings.postgis.password + ' host=' + deployment_settings.postgis.host + ' port=' + str (deployment_settings.postgis.port))

if deployment_settings.database.db_type == 'sqlite':
    db = DAL('sqlite://storage.sqlite', check_reserved=['all'])
else:
    dd = deployment_settings.database
    db = DAL (dd.db_type + '://' + dd.username + ':' + dd.password  + '@' + dd.host + '/' + dd.database, dd.pool_size, check_reserved=['all'])

crud = Crud(globals(), db)

if deployment_settings.mongodb.host:
    import pymongo
    from pymongo.objectid import ObjectId
    mongo = pymongo.Connection (deployment_settings.mongodb.host, deployment_settings.mongodb.port)[deployment_settings.mongodb.db]
    mongo.authenticate(deployment_settings.mongodb.username, deployment_settings.mongodb.password)
else:
    mongo = None

class MongoCursorWrapper:
    def __init__ (self, cursor):
        self.__cursor = cursor

    def __getattr__ (self, key):
        return getattr (self.__cursor, key)

    def __getitem__ (self, index):
        return MongoWrapper (self.__cursor[index])
        #return map (lambda x : MongoWrapper (x), self.__cursor[index])

    def __len__ (self):
        return self.__cursor.count ()
    
    def __iter__ (self):
        return MongoWrapperIter (self.__cursor)

class MongoWrapper:
    def __init__ (self, cursor):
        self.__dict__['cursor'] = cursor

    def __getattr__ (self, key):
        try:
            return getattr (self.cursor, key)
        except AttributeError:
            try:
                val = self.cursor[unicode (key)]
                if (type (val) == list) or (type (val) == dict):
                    return MongoWrapper (self.cursor[unicode (key)])
                else:
                    return val
            except KeyError:
                return None

    def __nonzero__ (self):
        if self.cursor is None:
            return False
        return len (self.cursor) != 0

    def __iter__ (self):
        return MongoWrapperIter (self.cursor)

    '''def __setattrbute__ (self, key, value):
        try:
            setattr (self.cursor, key)
        except AttributeError:
            self.cursor[unicode (key)]'''

class MongoWrapperIter:
    def __init__ (self, cursor):
        self.__cursor = iter (cursor)

    def __iter__ (self):
        return self

    def next (self):
        val = self.__cursor.next ()
        if (type (val) == list) or (type (val) == dict):
            return MongoWrapper (val)
        else:
            return val
