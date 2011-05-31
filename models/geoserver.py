from urllib import urlencode
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

def sync_geoserver (path):
    file = urlopen (path + '/wms?SERVICE=WMS&REQUEST=GetCapabilities')
    buffer = file.read ()
    soup = BeautifulStoneSoup (buffer)
    layers = soup.findAll (name = 'layer')
    results = []
    for l in layers:
        name = l.find ('title')
        id = l.find ('name')
        if name and id:
            text = name.string
            if not text:
                text = id.string
            m = match ('^([^\:]+)\:(.+)$', id.string)
            if m:
                p = m.group (1)
                f = m.group (2)
            else:
                p = '',
                f = id.string
            id = dm.insert ('maps', prefix = p, filename = f, name = text, src = path, public = True)
            keywords = l.findAll (name = 'keyword')
            kw = []
            for k in keywords:
                kw.append (k.string)
            dm.keywords ('maps', id, kw)
