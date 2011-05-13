class DisplaySettings (attr_dict):
    def __init__ (self, **settings):
        attr_dict.__init__ (self, **settings)
        self.default ('title', False)
        self.default ('name', None)
        self.default ('visible', True)



