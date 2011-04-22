from rpy2 import rinterface

libraries = []
rinterface.initr ()

def importLibrary (lib):
    if not lib in libraries:
        libraries.append (lib)
        rinterface.globalenv.get ('library') (rinterface.StrSexpVector ([lib]))

def R (func):
    rfunc = rinterface.globalenv.get (func)
    def f (*args, **kwargs):
        argList = []
        kwargDict = {}
        for a in args:
            argList.append (rType (a))
        for k, v in kwargs.iteritems ():
            kwargDict[k] = rType (v)
        rResult = rfunc (*argList, **kwargDict)
        length = len (rResult)
        #if not hasattr (rResult, '__iter__'):
        #    return None
        #if length == 0:
        #    return None
        #elif length == 1:
        #    return rResult[0]
        # else:
        results = []
        count = 0
        while count < length:
            results.append (rResult[count])
            count += 1
        return results
        """for x in rResult:
            results.append (x)
        if len (results) == 0:
            return None
        elif len (results) == 1:
            return results[0]
        else:
            return results"""
    return f

def rType (value):
    if not isinstance (value, list):
        value = [value]

    t = commonType (value)

    if t == list:
        v = rinterface.SexpVector (map (rType, value), rinterface.LISTSXP)
    elif t == float:
        v = rinterface.FloatSexpVector (value)
    elif t == int:
        v = rinterface.IntSexpVector (value)
    elif t == bool:
        v = rinterface.BoolSexpVector (value)
    elif t == str:
        v = rinterface.StrSexpVector (value)
    else:
        v = None
    return v

def commonType (elements):
    if len (elements) == 0:
        raise RuntimeError ('Empty list provided. Cannot create vector.')
    t = type (elements[0])
    for item in elements:
        if (t == float or t == int) and t != type (item):
            t = float
        elif t != type (item):
            raise RuntimeError ('No common type. Cannot create vector.')
    return t

"""class RInstance:
    def __getattr__ (self, key):
        print key
    
    def __setattr__ (self, key, value):
        pass

    def importLibrary (lib):
        pass

    def rType (primative):
        pass


R = RInstance ()"""

def r_vector_string (ob):
    if type (ob) == list:
        strings = []
        for o in ob:
            strings.append (r_vector_string (o))
        return 'c(' + ','.join (strings) + ')'
    else:
        return str (ob)
