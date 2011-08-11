import simplejson as json

def index():
    return {}

def wiki():
    from urllib2 import urlopen, Request
    from re import sub
    
    disease = request.vars.get ('disease')

    r = Request ('http://en.wikipedia.org/w/index.php?action=render&title=%s' % (disease,), headers = {'User-Agent': 'Healthscapes'})
    result = urlopen (r)
    html = result.read ()
    return sub ('(<table class\=\"infobox[^>]*style=")', '\\1float: left; margin-right: 10px;', html)

def npr():
    from urllib2 import urlopen

    disease = request.vars.get ('disease')

    result = urlopen ('http://api.npr.org/query?apiKey=' + deployment_settings.npr.key +'&fields=title,teaser&output=JSON&searchTerm=%s' % (disease,))

    return result.read ()


