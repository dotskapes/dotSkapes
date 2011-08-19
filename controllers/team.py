def index():
    images = team_db().select(team_db.image.ALL, orderby=team_db.image.category_id)
    return dict(images=images)

def download():
    return response.download(request, team_db)
