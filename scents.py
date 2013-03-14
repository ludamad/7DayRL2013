from geometry import *

class ScentMaps:
    def __init__(self, world, size):
        self.trailmap = ScentMap(size)
        self.resourcemap = ScentMap(size)
        self.avoidmap = ScentMap(size)
    def step(self):
        self.trailmap.decay()
    def trail(self,xy):
#        print "trail at x: %i y: %i" % (xy.x, xy.y)
#        print "oldval %i" % self.trailmap[xy]
        self.trailmap.add(xy, 5)
#        print "newval %i" % self.trailmap[xy]
    def avoid(self,xy):
        self.avoidmap.add(xy, 5)
    def add(self,xy):
        self.resourcemap.radius(xy, 5)
    def remove(self,xy):
        self.resourcemap.clear(xy, 15)

class ScentMap:
    def __init__(self, size):
        self.size = size
        self.map = [ [ 0 for x in range(size.w) ]
                        for y in range(size.h) ]
        self.decayrate = 1
        self.maxstrength = 15
    def rect(self):
        return make_rect( Pos(0,0), self.size )
    
    # To allow for a = map[xy]
    def __getitem__(self, xy):
        return self.map[ xy.y ][ xy.x ]

    # To allow for map[xy] = a
    def __setitem__(self, xy, strength):
        self.map[ xy.y ][ xy.x ] = strength

    def add(self, xy, strength):
        self[xy] = self[xy] + strength
        if self[xy] > self.maxstrength:
            self[xy] = self.maxstrength
    
    def remove(self, xy, strength):
        self[xy] = self[xy] - strength
        if self[xy] < 0:
            self[xy] = 0

    def decay(self):
        for xy in self.rect().xy_values():
            if self[xy] >= self.decayrate:
                self[xy] = self[xy] - self.decayrate
        