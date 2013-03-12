from geometry import *

class ScentMap:
    def __init__(self, world, size):
        self.world = world
        self.size = size
        self.trailmap = [ [ 0 for x in range(size.w) ]
                        for y in range(size.h) ]
        self.resmap = [ [ 0 for x in range(size.w) ]
                        for y in range(size.h) ]
        self.decay = 1
    def rect(self):
        return make_rect( Pos(0,0), self.size )
    def step(self,world):
        self.decay(self.trailmap)        
    def decay(self, map):
        for i in self.rect():
            if map[i] >= self.decay:
                map[i] = map[i] - self.decay
        