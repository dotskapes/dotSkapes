from spatial import SpatialList

class QuadTree:
    def __init__ (self):
        self.root = None

    def append (self, point):
        if not self.root:
            self.root = Treenode (point)
        else:
            self.root.append (point)

    def search (self, box):
        pointList = SpatialList ()
        self.root.search (pointList, box)
        return pointList


class Treenode:
    def __init__ (self, point):
        self.data = point
        self.first = None
        self.second = None
        self.third = None
        self.fourth = None

    def quadrant (self, point):
        if self.data.y <= point.y:
            if self.data.x <= point.x:
                return 1
            else:
                return 2
        else:
            if self.data.x >= point.x:
                return 3
            else:
                return 4

    def getNext (self, int):
        if int == 1:
            return self.first
        elif int == 2:
            return self.second
        elif int == 3:
            return self.third
        elif int == 4:
            return self.fourth

    def setNext (self, int, point):
        if int == 1:
            self.first = Treenode (point)
        elif int == 2:
            self.second = Treenode (point)
        elif int == 3:
            self.third = Treenode (point)
        elif int == 4:
            self.fourth = Treenode (point)

    def append (self, point):
        quad = self.quadrant (point)
        node = self.getNext (quad)
        if not node:
            self.setNext (quad, point)
        else:
            node.append (point)

    def search (self, pointList, box):
        if box.contains (self.data):
            pointList.append (self.data)
            for i in xrange (1, 5):
                node = self.getNext (i)
                if node:
                    node.search (pointList, box)
        else:
            num = []
            for vertex in box:
                num.append (self.quadrant (vertex))
            indices = set (num)
            for i in indices:
                node = self.getNext (i)
                if node: 
                    node.search (pointList, box)
