from globals import world
from geometry import *

class ScentMaps:
    def __init__(self, size):
        self.trailmap = ScentMap(size)
        self.resourcemap = ScentMap(size)
    def step(self):
        self.trailmap.decay()

class ScentMap:
    def __init__(self, size):
        self.size = size
        self.map = [ [ 0 for x in range(size.w) ]
                        for y in range(size.h) ]
        self.decayrate = 1
    def rect(self):
        return make_rect( Pos(0,0), self.size )
    
    # To allow for a = map[xy]
    def __getitem__(self, xy):
        return self.map[ xy.y ][ xy.x ]

    # To allow for map[xy] = a
    def __setitem__(self, xy, strength):
        self.map[ xy.y ][ xy.x ] = strength

    def decay(self):
        for xy in self.rect().xy_values():
            if self[xy] >= self.decayrate:
                self[xy] = self[xy] - self.decayrate
        