import gluon.contrib.simplejson as json

from geo import enum
from geo.tree import QuadTree 
from geo.func import get
from geo.utils import keygen
from savage.graphics.color import ColorMap, red, blue, green
 
cargs = [('boundry', 'Boundry Map', 'poly_map'),
         ('sort', 'Sort Field', 'attr', 'boundry'),
         ('points', 'Point Map', 'point_map'),
         ('agg', 'Aggregation', 'agg', 'points'),
         ('output', 'Output', 'select', 'Map', 'Graph', 'Table'),
         ('title', 'Title', 'text'),
         ('xlabel', 'X Label', 'text'),
         ('ylabel', 'Y Label', 'text')]

#rType = 'image/svg+xml'
#rType = 'text/html'

def keymap (keys, data):
    mapping = []
    for d in data:
        pair = (d[0], d[1])
        if keys.has_key (pair):
            mapping.append (keys[pair]) 
        else:
            mapping.append (d[1])
    return mapping

def ctool (**attr):
    polygons = attr['boundry']
    points = attr['points']

    pointTree = QuadTree ()
    for p in points:
        pointTree.append (p)

    for poly in polygons:
        poly.insert (poly.contains (pointTree))

    keys = {}
    output = []

    aggSource = attr['agg']['map']
    dataSource = attr['agg']['data']
    for inst in dataSource:
        dst = keygen (inst['name'])
        if inst['output']:
            output.append (dst)
        for poly in polygons:
            keys[(None, inst['name'])] = dst
            src = keymap (keys, inst['data'])
            func = get (str (inst ['method']), attr['points'])
            if inst['dir'] == 'extern':
                mode = enum.MANY_TO_ONE
            else:
                mode = enum.ONE_TO_ONE
            poly.compute (mode, func, dst, *src)

    if attr['output'] == 'Graph':
        polygons.bar_graph (attr['file'], attr['sort'], output, title = attr['title'], xlabel = attr['xlabel'], ylabel = attr['ylabel'])
        return 'image/svg+xml'

    elif attr['output'] == 'Map':
        polygons.reduce (output[0])
        cm = ColorMap (blue, red, len (polygons))
        polygons.sort (output[0])
        for i, p in enumerate (polygons):
            p.color (cm.index (i))
        polygons.svg (attr['file'])
        return 'image/svg+xml'

    elif attr['output'] == 'Table':
        polygons.html_table (attr['file'])
        #polygons.html_table (attr['file'], output)
        return 'text/html'

    """poly_map = attr['boundry']
    sort_key = poly_map.addSortField (attr['sort'])
    polygons = poly_map.load ();
    for pname, poly in polygons:
        poly.transform (enum.SPATIAL)

    toGraph = []
    loadFields = {}
    for inst in attr['agg']:
        ob = json.loads (inst['data'])
        groupKey = Group (inst['name'])
        loadFields[(None, inst['name'])] = groupKey       
        for data in ob:
            source = data[0]
            name = data[1]
            if source:
                key = point_map.addField (name)
            else:
                key = Group (name)
            loadFields[(source, name)] = key
        if inst['dir'] == 'extern':
            toGraph.append (groupKey)
       
    points = point_map.load ()
    points.transform (enum.SPATIAL)
    
    polygons.push (points)

    instList = []

    for g in attr['agg']:
        ob = json.loads (g['data'])
        groupKey = loadFields[(None, g['name'])]
        params = []
        for data in ob:
            source = data[0]
            name = data[1]
            params.append (loadFields[(source, name)])
        if g['dir'] == 'extern':
            mode = enum.EXTERN
        elif g['dir'] == 'intern':
            mode = enum.INTERN

        if g['method'] == 'Mean':
            method = getFunction (enum.MEAN)
        elif g['method'] == 'Sum':
            method = getFunction (enum.SUM)            

        inst = Instruction (mode, method, groupKey, *params)
        instList.append (inst)

    polygons.compute (instList)

    returnList =  ''
    for pname, poly in polygons:
        val = ''
        for k, v in poly:
            val += str (k) + ' - ' + str (v) + ' '
        returnList += (str (pname) + ': ' + val) + '<br />'

    barGraphData (attr['file'], polygons, toGraph)"""
