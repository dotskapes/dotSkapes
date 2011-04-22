def SUM (*args):
    value = 0.0
    for a in args:
        value += float (a)
    return value 

def SUB (arg1, arg2):
    return (arg1 - arg2)

def MEAN (*args):
    return SUM (*args) / float (len (args))

def NONZERO (arg):
    if arg == 0:
        return None
    else:
        return arg

'''def makeCount (src):
    def COUNT (*args):
        count = 0
        for a in args:
            if a == src:
                count += 1
        return count
    return COUNT'''

def COUNT (*args):
    return len (args)

def MIN (*args):
    return min (args)

def MAX (*args):
    return max (args)

def get (name, *args):
    name = str (name)
    if name == 'MEAN':
        return MEAN
    elif name == 'SUM':
        return SUM
    elif name == 'SUB':
        return SUB
    elif name == 'NONZERO':
        return NONZERO
    elif name == 'COUNT':
        #return makeCount (*args)
        return COUNT
    elif name == 'MIN':
        return MIN
    elif name == 'MAX':
        return MAX
