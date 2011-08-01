def get_arg (val):
    if not val:
        return (None, None)
    arg = val.split ('.')
    return (arg[0], '.'.join (arg[1:]))
