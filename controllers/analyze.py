def index():
    return {}

def tool():
    response.view = 'analyze/index.html'
    return {'tool': dm.get ('tools', request.args (0)).public ()}
