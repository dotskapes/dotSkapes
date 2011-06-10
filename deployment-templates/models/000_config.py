import psycopg2

class blank (object):
    def __init__ (self):
        object.__init__ (self)

deployment_settings = blank ()

# Database settings
deployment_settings.database = blank ()
deployment_settings.database.db_type = "sqlite"
deployment_settings.database.host = "localhost"
deployment_settings.database.port = 5432
deployment_settings.database.database = "data"
deployment_settings.database.username = "admin"
deployment_settings.database.password = "passwd"
deployment_settings.database.pool_size = 30

# Data Manager Settings
deployment_settings.data = blank ()
deployment_settings.data.base_table = "base_data_table"

# PostGIS Settings
deployment_settings.postgis = blank ()
deployment_settings.postgis.host = "localhost"
deployment_settings.postgis.port = 5432
deployment_settings.postgis.database = "postgis"
deployment_settings.postgis.username = "admin"
deployment_settings.postgis.password = "passwd"
deployment_settings.postgis.pool_size = 10
deployment_settings.postgis.connection = lambda: psycopg2.connect ('dbname=' + deployment_settings.postgis.database + ' user=' + deployment_settings.postgis.username + ' password=' + deployment_settings.postgis.password + ' host=' + deployment_settings.postgis.host + ' port=' + str (deployment_settings.postgis.port))

#Geoserver Settings
deployment_settings.geoserver_sources = ["http://path/to/geoserver",]

deployment_settings.geoserver = blank ()
deployment_settings.geoserver.url = "localhost"
deployment_settings.geoserver.username = "admin"
deployment_settings.geoserver.password = "passwd"
deployment_settings.geoserver.wms_capabilities = lambda: deployment_settings.geoserver.url + '/wms?SERVICE=WMS&REQUEST=GetCapabilities'

# NPR Settings
deployment_settings.npr = blank ()
deployment_settings.npr.key = 'register_for_an_npr_key'
