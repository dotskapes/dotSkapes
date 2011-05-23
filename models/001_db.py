# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

if deployment_settings.database.db_type == 'sqlite':
    db = DAL('sqlite://storage.sqlite')
else:
    dd = deployment_settings.database
    db = DAL (dd.db_type + '://' + dd.username + '@' + dd.host + '/' + dd.database, dd.pool_size)
