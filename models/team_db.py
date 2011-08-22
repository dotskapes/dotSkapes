team_db = DAL("sqlite://storage.sqlite")

team_db.define_table('category',
   Field('title'),
   Field('div_id'),
   Field('priority'))

team_db.define_table('image',
   Field('category_id', team_db.category),
   Field('last_name'),
   Field('first_name'),
   Field('email'),
   Field('website'),
   Field('file', 'upload'))

team_db.image.category_id.requires = IS_IN_DB(team_db, team_db.category.id, '%(title)s')
