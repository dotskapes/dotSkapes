from ..graphics import Canvas
from ..graphics.shapes import Text, Square

class Legend (Canvas):
    def __init__ (self, **attr):
        Canvas.__init__ (self, **attr)
        if attr.has_key ('textHeight'):
            self.textHeight = attr['textHeight']
        else:
            self.textHeight = 10
        self.side1 = 0
        self.side2 = 0
        #self.lineWidth = self.width / 2.0 - 30.0
        self.height = 0.0
        self.lineWidth = self.width - 30
        
    def addKey (self, key, color):
        currentX = 0.0
        s = Square (8, x = currentX + 10, y = self.height)
        s.style.fill = color
        self.draw (s)
        line = Text (text = key,
                     x = currentX + 20,
                     y = self.height,
                     textHeight = self.textHeight,
                     lineLength = self.lineWidth,
                     maxLines = 2,
                     direction = 'forward',
                     )
        self.draw (line)
        self.height += line.height + 3
        """if self.side1 <= self.side2:
            currentX = 0
            yValue = self.side1
        else:
            currentX = self.width / 2.0
            yValue = self.side2
        s = Square (8, x = currentX + 10, y = yValue)
        s.style.fill = color
        self.draw (s)
        line = Text (text = key,
                     x = currentX + 20,
                     y = yValue,
                     textHeight = self.textHeight,
                     lineLength = self.lineWidth,
                     direction = 'forward',
                     )
        if self.side1 <= self.side2:
            self.side1 += line.height + 3
        else:
            self.side2 += line.height + 3
        self.draw (line)
        self.height = max (self.side1, self.side2)"""
