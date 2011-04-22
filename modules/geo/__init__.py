from spatial import Spatial, SpatialList
from r import importLibrary, R, r_vector_string

class Map (SpatialList):
    def addFeature (self, feature):
        self.append (feature)

    """def r (self, name):
        data = {}
        for f in self:
            for k in f:
                if not data.has_key (k):
                    data[k] = []

        for f in self:
            for key, value in data.iteritems ():
                if f.has_key (key):
                    if type (f[key]) != float and type (f[key]) != int:
                        value.append ('"' + str (f[key]) + '"')
                    else:
                        value.append (str (f[key]))
                else:
                    value.append ('NA')

        #data['geometry'] = []

        #for f in self:
        #    data['geometry'].append (f.r_geometry ())

        kw = []
        for key, value in data.iteritems ():
            kw.append (str (key) + '=' + r_vector_string (value))

        return str(name) + '=data.frame(' + ','.join (kw)  + ')'"""

    def html_table (self, filename, keys = None):
         if type (filename) == str:
             close = True
             filename = open (filename, 'w')
         else:
             close = False
         if keys is None:
             keys = set ()
             for f in self:
                 k = set (f.keys ())
                 keys |= k
         filename.write ("""
<style>
body {
  font-family: sans-serif;
}
table {
  text-align: center; 
  vertical-align: middle; 
  margin: 0px;
  border-collapse: collapse;
}
th {
  background-color: #6666ff;
  padding: 15px 10px;
  color: white;
  font-weight: bold;
  border: 1px solid #66aaff;
}
td {
  border: 1px solid #66aaff;
  padding: 10px;
}

tr.even {
  background-color: #eeeeee;
}

tr.odd {
  background-color: #cccccc;
}
</style>
""")
         filename.write ('<table cellspacing="0"><tr>')
         for k in keys:
             filename.write ('<th>' + str (k) + '</th>')
         filename.write ('</tr>')
         for i, f in enumerate (self):
             if (i % 2) == 0:
                 mod2 = 'even'
             else: 
                 mod2 = 'odd'
             filename.write ('<tr class="' + mod2 + '">')
             for k in keys:
                 if f.has_key (k):
                     val = str (f[k])
                 else:
                     val = 'NA'
                 filename.write ('<td>' + val + '</td>')
             filename.write ('</tr>')
         filename.write ('</table>')
         if close:
             filename.close ()

    def bar_graph (self, filename, sort, groups, title = None, xlabel = None, ylabel = None, 
                   settings = None, colors = None):
        from savage.graph import BarGraph
        #settings['horizontal'] = True
        graph = BarGraph (settings = settings)
        if xlabel:
            graph.setXLabel (xlabel)
        if ylabel:
            graph.setYLabel (ylabel)
        if title:
            graph.setTitle (title)
        if colors:
            graph.setColors (colors)
        for row in self:
            rname = row[sort]
            groupData = []
            for key in groups:
                try:
                    value = row[key]
                    groupData.append ((key, value))
                except KeyError:
                    continue
            if len (groupData)> 0:
                if len (groups) > 1:
                    graph.addGroup (rname, groupData)
                else:
                    graph.addBar (rname, groupData[0][1])
        graph.save (filename)        

    def svg (self, filename):
        from savage.graphics import PrintableCanvas
        from savage.graphics.utils import ViewBox
        view = None
        for f in self:
            if not view:
                view = f.bounds ()
            else:
                view = view.union (f.bounds ())
        v = ViewBox (view.minPoint.x, view.minPoint.y, view.maxPoint.x, view.maxPoint.y)
        canvas = PrintableCanvas (viewBox = v)
        canvas.invertY ()
        for f in self:
            canvas.draw (f.svg ())
        canvas.save (filename)


class Polygon (Spatial):
    def __init__ (self, geom, data):
        Spatial.__init__ (self, data)
        self.simplePolygons = []
        for s in geom:
            self.simplePolygons.append (SimplePolygon (s))
        self.features = []
        self.db = None
    
    def contains (self, pointTree):
        points = set ()
        importLibrary ('sp')
        for s in self.simplePolygons:
            pointList = pointTree.search (s.bounds ())
            vx = []
            vy = []
            for p in pointList:
                vx.append (p.x)
                vy.append (p.y)
            if len (vx) == 0:
                continue
            locations = R ('point.in.polygon') (vx, vy, s.x, s.y)
            for i, val in enumerate(locations):
                if val != 0:
                    points.add (pointList[i])
        return points

    def compute (self, mode, func, dst, *src):
        if mode == enum.ONE_TO_ONE:
            Spatial.compute (self, mode, func, dst, *src)
            for f in self.features:
                f.compute (mode, func, dst, *src)
        elif mode == enum.MANY_TO_ONE:
            params = []
            for f in self.features:
                for s in src:
                    if f.has_key (s):
                        params.append (f[s])
            if len (params) > 0:
                self[dst] = func (*params)

    def equals (self, poly):
        pass

    def insert (self, points):
        for p in points:
            self.features.append (p)

    def geometry (self):
        geom = []
        for s in self.simplePolygons:
            geom.append (s.geometry ())
        return geom

    def bounds (self):
        bound = None
        for s in self.simplePolygons:
            if not bound:
                bound = s.bounds ()
            else:
                bound = bound.union (s.bounds ())
        return bound

    def color (self, c):
        for s in self.simplePolygons:
            s.color = c

    def svg (self):
        from savage.graphics.group import Group
        g = Group ()
        for s in self.simplePolygons:
            g.draw (s.svg ())
        return g


class SimplePolygon:
    def __init__ (self, coords):
        self.color = None
        self.x = []
        self.y = []
        for pair in coords:
            self.x.append (pair[0])
            self.y.append (pair[1])
        self.bound = BoundingBox ((min (self.x), min (self.y)), (max (self.x), max (self.y)))

    def geometry (self):
        return zip (self.x, self.y)

    def bounds (self):
        return self.bound

    def svg (self):
        from savage.graphics.shapes import Path
        shape = Path ()
        shape.style.strokeColor = 'none'
        if self.color:
            shape.style.fill = self.color
        anchor = False
        for point in self.geometry ():
            if not anchor:
                shape.move (*point)
                anchor = True
            else:
                shape.line (*point)
        shape.close ()
        return shape


class Point (Spatial):
    def __init__ (self, geom, data = []):
        Spatial.__init__ (self, data)
        self.x = geom[0]
        self.y = geom[1]


class Line (Spatial):
    pass


class BoundingBox:
    def __init__ (self, pair1, pair2):
        x1 = min (pair1[0], pair2[0])
        y1 = min (pair1[1], pair2[1])
        x2 = max (pair1[0], pair2[0])
        y2 = max (pair1[1], pair2[1])

        self.p1 = Point ((x1, y1))
        self.p2 = Point ((x1, y2))
        self.p3 = Point ((x2, y2))
        self.p4 = Point ((x2, y1))

        self.minPoint = self.p1
        self.maxPoint = self.p3

        self.points = [self.p1, self.p2, self.p3, self.p4]

    def union (self, box):
        x1 = min (self.minPoint.x, box.minPoint.x)
        y1 = min (self.minPoint.y, box.minPoint.y)
        x2 = max (self.maxPoint.x, box.maxPoint.x)
        y2 = max (self.maxPoint.y, box.maxPoint.y)
        return BoundingBox ((x1, y1), (x2, y2))  

    def contains (self, point):
        if point.x < self.p1.x:
            return False
        if point.x > self.p3.x:
            return False
        if point.y < self.p1.y:
            return False
        if point.y > self.p3.y:
            return False
        return True        

    def __iter__ (self):
        return iter (self.points)
