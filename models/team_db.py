team_db = DAL("sqlite://storage.sqlite")

team_db.define_table('category',
	Field('category'))

team_db.define_table('people',
	Field('group_id', team_db.category),
	Field('first_name'),
	Field('last_name'),
	Field('email'),
	Field('body', 'text'))

team_db.define_table('image',
	Field('people_id', team_db.people),
	Field('file', 'upload'))



