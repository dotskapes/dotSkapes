# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

if deployment_settings.database.db_type == 'sqlite':
    db = DAL('sqlite://storage.sqlite', check_reserved=['all'])
else:
    dd = deployment_settings.database
    db = DAL (dd.db_type + '://' + dd.username + ':' + dd.password  + '@' + dd.host + '/' + dd.database, dd.pool_size, check_reserved=['all'])
