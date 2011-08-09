class blank (object):
    def __init__ (self):
        object.__init__ (self)

deployment_settings = blank ()

# Web2py Settings
deployment_settings.web2py = blank ()
deployment_settings.web2py.port = 8000

# Database settings
deployment_settings.database = blank ()
deployment_settings.database.db_type = "sqlite"
deployment_settings.database.host = "localhost"
deployment_settings.database.port = None # use default
deployment_settings.database.database = "healthscapes"
deployment_settings.database.username = "hs"
deployment_settings.database.password = "hs"
deployment_settings.database.pool_size = 30

# MongoDB Settings
deployment_settings.mongodb = blank ()
deployment_settings.mongodb.host = None
deployment_settings.mongodb.port = 27017
deployment_settings.mongodb.db = 'mongo_db'
deployment_settings.mongodb.username = 'mongo'
deployment_settings.mongodb.password = 'mongo'

# PostGIS Settings
deployment_settings.postgis = blank ()
deployment_settings.postgis.host = None
deployment_settings.postgis.port = 5432
deployment_settings.postgis.database = "geodata"
deployment_settings.postgis.username = "postgis"
deployment_settings.postgis.password = "postgis"
deployment_settings.postgis.pool_size = 10

deployment_settings.geoserver_sources = []

# Upload Geoserver Settings
deployment_settings.geoserver = blank ()
deployment_settings.geoserver.host = 'http://localhost'
deployment_settings.geoserver.port = 8888
deployment_settings.geoserver.username = "admin"
deployment_settings.geoserver.password = "geoserver"
deployment_settings.geoserver.workspace = 'hsd'
deployment_settings.geoserver.pgis_store = 'test'

# NPR Settings
deployment_settings.npr = blank ()
deployment_settings.npr.key = 'MDA2OTc4ODY2MDEyOTc0NTMyMjFmZGNjZg001'

deployment_settings.data = blank ()
deployment_settings.data.base_table = 'datatypes'

# Development Mode
deployment_settings.dev_mode = blank ()
deployment_settings.dev_mode.enabled = False
deployment_settings.dev_mode.firstname = 'First'
deployment_settings.dev_mode.lastname = 'Last'
deployment_settings.dev_mode.email = 'fake@gmail.com'

# ExtJS Settings
deployment_settings.extjs = blank ()
deployment_settings.extjs.location = 'http://skapes.org/media/js/ext'
