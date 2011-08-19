def index(): 
	images = team_db().select(team_db.image.ALL)
	return dict(images=images)
