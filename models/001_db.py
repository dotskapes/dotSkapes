# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

if deployment_settings.database.db_type == 'sqlite':
    db = DAL('sqlite://storage.sqlite')
else:
    dd = deployment_settings.database
    db = DAL (dd.db_type + '://' + dd.username + '@' + dd.host + '/' + dd.database, dd.pool_size)

from gluon.tools import *
auth = Auth(globals(), db)                     

auth.define_tables()                          

auth.settings.create_user_groups = False
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.register_next = URL (a = request.application, c = 'default',  f = 'register')
auth.settings.login_next = URL (a = request.application, c = 'default',  f = 'index.html')

table = auth.settings.table_group
if not db(db[table].id > 0).count():
    admin_role = auth.add_group ("Administrator", "System Administrator - can access & make changes to any data")
    dev_role = auth.add_group ("Developer", "Developer - Users with development privileges")
    auth_role = auth.add_group ("Authenticated", "Authenticated - all logged-in users")
else:
    admin_role = auth.id_group ("Administrator")
    dev_role = auth.id_group ("Developer")
    auth_role = auth.id_group ("Authenticated")

'''
auth.settings.hmac_key = '<your secret key>'   # before define_tables()
#auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'
'''
