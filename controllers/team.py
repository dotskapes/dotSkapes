def index():
    images = team_db().select(team_db.image.ALL, orderby=team_db.image.category_id)
    categories = team_db().select(team_db.category.ALL, orderby=team_db.category.priority)
    return dict(images=images, categories=categories)

def download():
    return response.download(request, team_db)
