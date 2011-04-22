from utils import ordered_dict
import enum

class Spatial (ordered_dict):
    def __init__ (self, data):
        ordered_dict.__init__ (self, data)

    def compute (self, mode, func, dst, *src):
        if mode == enum.ONE_TO_ONE:
            for s in src:
                if not self.has_key (s):
                    return
            params = map (lambda x: self[x], src)
            self[dst] = func (*params)

    def __eq__ (self, ob):
        return id (self) == id (ob)

    def __hash__ (self):
        return id (self)


class SpatialList (list):
    def __init__ (self, data = [], name = None):
        self.name = name
        list.__init__ (self, data)

    def reduce (self, key):
        remove = []
        for val in self:
            if not val.has_key (key):
                remove.append (val)

        for item in remove:
            self.remove (item)

    def sort (self, val):
        list.sort (self, key = lambda x: x[val])

    def dict (self, key):
        keys = map (lambda x: x[key], self)
        pairs = zip (keys, self)
        return SpatialDict (pairs)


class SpatialDict (ordered_dict):
    def __init__ (self, data):
        ordered_dict.__init__ (self, data)
        
    def sort (self, val):
        self._keys.sort (key = lambda x: x[val])
