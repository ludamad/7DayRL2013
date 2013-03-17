from geometry import *
from gameobject import GameObject

class ScentObject(GameObject):
    def __init__(self, xy, tile, strength, radius=3, time_to_live=50):
        GameObject.__init__(self, xy, tile, solid=False, draw_once_seen=True)
        self.strength = strength
        self.radius = radius
        self.time_to_live = time_to_live
    def apply_scent(self, scents):
        scents.apply_scent(self.xy, self.strength, radius=self.radius)
    def step(self):
        from globals import world
    
        self.time_to_live -= 1
        for obj in world.level.objects_at(self.xy):
            if obj == world.player:
                world.level.queue_removal(self)
                return
        if self.time_to_live <= 0:
            world.level.queue_removal(self)

class ScentMaps:
    def __init__(self, world, size):
        self.towards_map = ScentMap(size) # eg, resources attract
        self.return_map = ScentMap(size) # eg, ant colony attracts

        self.left = ScentMap(size)
        self.right = ScentMap(size)
        self.up = ScentMap(size)
        self.down = ScentMap(size)
        self.directionals = [self.left, self.right, self.up, self.down]

    def step(self):
        from globals import world
        self.towards_map.clear()
        self.return_map.clear()
        for dir in self.directionals:
            dir.decay()
        for obj in world.level.objects:
            obj.apply_scent(self)

    def trail(self, from_xy, to_xy, going_towards):
        delta = (to_xy - from_xy) * (+1 if going_towards else -1)
        if delta.x < 0: self.left.add(to_xy, 5)
        if delta.x > 0: self.right.add(to_xy, 5)
        if delta.y < 0: self.up.add(to_xy, 5)
        if delta.y > 0: self.down.add(to_xy, 5)
                
    def apply_scent(self, xy, strength, radius=3):
        self.apply_scent_towards(xy, strength, radius)
        self.apply_scent_return(xy, strength, radius)

    def apply_scent_towards(self, xy, strength, radius=3):
        self.towards_map.apply_scent(xy, strength, radius)

    def apply_scent_return(self, xy, strength, radius=3):
        self.return_map.apply_scent(xy, strength, radius)

    def get_scent_strength(self, from_xy, to_xy, going_towards):
        scent = 0
        delta = (to_xy - from_xy) if going_towards else (from_xy - to_xy)

        if delta.x < 0: scent+=self.left[to_xy]
        if delta.x > 0: scent+=self.right[to_xy]
        if delta.y < 0: scent+=self.up[to_xy]
        if delta.y > 0: scent+=self.down[to_xy]

        if going_towards: scent+=self.towards_map[to_xy]
        else: scent+=self.return_map[to_xy]

        return scent
        

class ScentMap:
    def __init__(self, size):
        self.size = size
        self.map = [ [ 0 for x in range(size.w) ]
                        for y in range(size.h) ]
        self.decayrate = 1
        self.maxstrength = 35
    def rect(self):
        return make_rect( Pos(0,0), self.size )
    
    # To allow for a = map[xy]
    def __getitem__(self, xy):
        return self.map[ xy.y ][ xy.x ]

    # To allow for map[xy] = a
    def __setitem__(self, xy, strength):
        self.map[ xy.y ][ xy.x ] = strength

    def clear(self):
        for xy in self.rect().xy_values():
            self[xy] = 0

    def add(self, xy, strength):
        self[xy] = self[xy] + strength
        if self[xy] > self.maxstrength:
            self[xy] = self.maxstrength

    def apply_scent(self, xy, strength, radius):
        from globals import world
        points = [ (x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
        strength_decay = (-strength / (radius+1))
        for x,y in points:
            p = xy +Pos(x,y)
            if world.level.map.valid_xy(p):
                dist = max( abs(x), abs(y) ) * strength_decay
                self[p] += dist + strength

    def decay(self):
        for xy in self.rect().xy_values():
            if self[xy] >= self.decayrate:
                self[xy] = self[xy] - self.decayrate


