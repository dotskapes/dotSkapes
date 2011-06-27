while True:
    user1 = raw_input ('Enter admin email address: ')
    user2 = raw_input ('Re-enter admin email address: ')
    if user1 != user2:
        print 'Email addresses do not match'
    else:
        break

admin_role = auth.add_group ("Administrator", "System Administrator - can access & make changes to any data")
dev_role = auth.add_group ("Developer", "Developer - Users with development privileges")
auth_role = auth.add_group ("Authenticated", "Authenticated - all logged-in users")
writer_role = auth.add_group ("Writer", "Writer - Can post to the blog")
editor_role = auth.add_group ("Editor", "Writer - Can post to and edit entries in the blog")

result = db (db[auth.settings.table_user_name].email == user1).select ().first ()
if result:
    user_id = result.id
else:
    user_id = db[auth.settings.table_user_name].insert (email = user1)
auth.add_membership (admin_role, user_id)

# Simmulate Login
auth.user = blank ()
auth.user.id = user_id

for geoserver in deployment_settings.geoserver_sources:
    sync_geoserver (geoserver)

db.commit ()
