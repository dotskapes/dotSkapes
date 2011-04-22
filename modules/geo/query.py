import psycopg2
from re import sub
from uuid import uuid4
from copy import copy, deepcopy

class DBConnection:
    def __init__ (self, 
                  db = None, 
                  user = 'postgres', 
                  passwd = None, 
                  host = 'localhost', 
                  port = 5432):
        self.db = db
        self.host = host
        connString = 'dbname=%s user=%s password=%s host=%s port=%s' % (db, user, passwd, host, port)
        self.connection = psycopg2.connect (connString)

    """def __eq__ (self, conn):
        if (self.db == conn.db) and (self.host == conn.host):
            return True
        else:
            return False"""

    def cursor (self):
        return self.connection.cursor ()


class TableField:
    def __init__ (self, name, conn, dblink):
        self.name = name
        self.conn = conn
        self.dblink = dblink
        self.id = '__table__' + str (uuid4 ().int)


class QueryField:
    def __init__ (self, name, fieldType, table):
        self.name = name
        self.type = fieldType
        self.table = table
        self.id = '__field__' + str (uuid4 ().int)


class QuerySet:
    def __init__ (self, conn):
        self.conn = conn
        self.selectList = []
        self.fromList = {}

    def __copy__ (self):
        q = QuerySet (self.conn)
        q.selectList = deepcopy (self.selectList)
        q.fromList = deepcopy (self.fromList)
        return q

    def select (self, table, conn = None):
        newQuery = copy (self)
        table = sub ("\W", "", table)
        if conn == None:
            conn = newQuery.conn

        if conn == newQuery.conn:
            mainDB = True
        else:
            mainDB = False

        pair= (table, conn)
        if newQuery.fromList.has_key (pair):
            #tableID = self.fromList[pair]
            raise RuntimeError ("Can not select the same table twice")
        else:
            newTable = TableField (table, conn, not mainDB)
            tableID = newTable.id
            newQuery.fromList[pair] = newTable

        sqlString = """SELECT column_name, udt_name 
                       FROM information_schema.columns 
                       WHERE table_name = '%s';""" % table
        cursor = conn.cursor ()
        cursor.execute (sqlString)
        fields = []
        for entry in cursor:
            key, value = entry
            fields.append (QueryField (key, value, tableID))
        newQuery.selectList += fields
        return newQuery

    def limit (self, *fields):
        pass
    
    def exclude (self, *fields):
        pass

    #def FROM (self, tablename):
    #    pass

    def load (self):
        pass

    def __iter__ (self):
        pass

    def __str__ (self):
        return """SELECT %s FROM %s""" % (toSelect (self.selectList), toFrom (self.fromList))

    def load (self):
        cursor = self.conn.cursor ()
        cursor.execute (str (self))
        print str (self)
        #for entry in cursor:
        #    print entry

def query (conn):
    return QuerySet (conn)

def selectEntry (field):
    if field.type == 'geometry':
        return 'AsText (' + field.table + '.'+ field.name + ')' + ' AS ' + field.id
    else:
        return field.table + '.'+ field.name + ' AS ' + field.id

def toSelect (list):
    return ', '.join (map (selectEntry, list))

def fromEntry (table):
    if table.dblink:
        raise NotImplemeneted ()
    else:
        return table.name + ' ' + table.id

def toFrom (list):
    return ', '.join (map (fromEntry, list.values ()))

def ST_Contains (geom1, geom2):
    pass

if __name__ == '__main__':
    conn = DBConnection (db='g4wd', passwd='aaa', port=5433)
    query (conn).select ('brazil').load ()
