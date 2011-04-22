from enum import Key

def keygen (name):
    return Key (name)

class ordered_dict (dict):
    def __init__ (self, data):
        dict.__init__(self, data)
        self._keys = dict.keys (self)

    def keys (self):
        return self._keys
    
    def update (self, pairs):
        try:
            for key, value in pairs.iteritems ():
                if not self.has_key (key):
                    self._keys.append (key)
        except AttributeError:
            for pair in pairs:
                if not self.has_key (pair[0]):
                    self._keys.append (pair[0])                   
        dict.update (self, pairs)

    def __setitem__ (self, key, value):
        if not self.has_key (key):
            self._keys.append (key)
        dict.__setitem__ (self, key, value)

    def __iter__ (self):
        return iter (self._keys)

    def iteritems (self):
        return ordered_dict_iterator (self, iter(self._keys))

class ordered_dict_iterator:
    def __init__ (self, dictionary, listIter):
        self._dictionary = dictionary
        self._listIter = listIter
        
    def __iter__ (self):
        return self

    def next (self):
        key = self._listIter.next ()
        return (key, self._dictionary[key])

class BoundingBox:
    def __init__ (self, x1, y1, x2, y2):
        self.p1 = Point ((x1, y1))
        self.p2 = Point ((x1, y2))
        self.p3 = Point ((x2, y2))
        self.p4 = Point ((x2, y1))
        self.points = [self.p1, self.p2, self.p3, self.p4]

    def contians (self, point):
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
