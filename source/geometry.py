import math

# Lots of ugly operator overloading, but it makes the rest of the code prettier.

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def distance(self, pos):
        dx, dy = pos.x - self.x, pos.y - self.y
        return math.sqrt(dx*dx+dy*dy)
    
    def sqr_distance(self, pos):
        dx, dy = pos.x - self.x, pos.y - self.y
        return max(abs(dx), abs(dy))
    def __add__(self, pos): 
        return Pos(self.x+pos.x, self.y+pos.y)
    def __sub__(self, pos): 
        return Pos(self.x-pos.x, self.y-pos.y)
    def __mul__(self, pos): 
        return Pos(self.x*pos.x, self.y*pos.y)
    def __div__(self, pos): 
        return Pos(float(self.x)/pos.x, float(self.y)/pos.y)
    def __eq__(self, pos):
        if type(self) != type(pos): return False
        return self.x == pos.x and self.y == pos.y
    def __ne__(self, pos):
        return not (self == pos)
    def __str__(self):
        return "Pos(" + str(self.x) + ", " + str(self.y) + ")"


class Size:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def __add__(self, size): 
        return Size(self.w+size.w, self.h+size.h)
    def __sub__(self, size): 
        return Size(self.w-size.w, self.h-size.h)
    def __mul__(self, size): 
        return Size(self.w*size.w, self.h*size.h)
    def __div__(self, size): 
        return Size(float(self.w)/size.w, float(self.h)/size.h)
    def __eq__(self, size):
        if type(self) != type(size): return False
        return self.w == size.w and self.h == size.h
    def __ne__(self, size):
        return not (self == size)
    def __str__(self):
        return "Size(" + str(self.w) + ", " + str(self.h) + ")"

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    # Iterates the range of x to x + width
    def x_values(self): return range(self.x, self.x + self.w)
    # Iterates the range of y to y + height
    def y_values(self): return range(self.y, self.y + self.h)
    # Iterates all the values of the rectangle
    def xy_values(self): return ( Pos(x,y) for y in self.y_values() for x in self.x_values() )

    def edge_values(self):
        for x in self.x_values(): 
            yield Pos(x, self.y)
            yield Pos(x, self.y + self.h - 1)
        for y in range(self.y+1, self.y-1 + self.h): 
            yield Pos(self.x, y)
            yield Pos(self.x + self.w - 1, y)

    def top_left(self): return Pos(self.x,self.y)

    def bottom_right(self): return Pos(self.x+self.w-1, self.y+self.h-1)

    def padding(self, pad): return Rect(self.x - pad, self.y - pad, self.w + pad * 2, self.h + pad * 2)

    def center(self):
        center_x = self.x + int(self.x2 / 2)
        center_y = self.y + int(self.y2 / 2)
        return Pos(center_x, center_y)
 
    def __add__(self, pos): 
        return Rect( self.x + pos.x, self.y + pos.y, 
                     self.w, self.h)
    def within(self, xy):
        return xy.x >= self.x and xy.x < self.x + self.w and xy.y >= self.y and xy.y < self.y + self.h
    # Returns true if this rectangle intersects with another one
    def intersects(self, other):
        return (self.x < other.x+other.w and self.x+self.w > other.x and
                self.y < other.y+other.h and self.y+self.h > other.y)

    def __eq__(self, rect):
        if type(self) != type(rect): return False
        return self.x == rect.x and self.y == rect.y and self.w == rect.w and self.h == rect.h
    def __ne__(self, rect):
        return not (self == rect)
    def __str__(self):
        return "Rect( x=" + str(self.x) + ", y=" + str(self.y) + ", w="  + str(self.w) + ", h=" + str(self.h) + ")"

def make_rect(pos, size):
    return Rect(pos.x, pos.y, size.w, size.h)