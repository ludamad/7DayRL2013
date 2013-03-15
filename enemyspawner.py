from utils import *
from geometry import *

def default_spawn_chances():
    from enemies import Enemy, ant, ladybug, roach, beetle
    return [65, ant, 25, ladybug, 50, roach, 7, beetle]

def spawn_with_weights(*args):
    def spawner(xy):
        from globals import world

        total = 0
        for i in range(0, len(args), 2):
            total += args[i]

        chance = rand(0, total-1)
        for i in range(0, len(args), 2):
            type, weight = args[i+1], args[i]
            chance -= weight
            if chance <= 0:
                # 'add_to_back_of_corpses' is a hack, but oh well
                world.level.add_to_back_of_corpses( type(xy) )
                return True
    return spawner

default_spawner = spawn_with_weights( *default_spawn_chances() )

# Closures, yay
def spawn_if_none_within(spawn_func = default_spawner, radius=1):
    def spawner(xy):
        from enemies import Enemy
        from globals import world
        points = [ xy + Pos(x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
        for p in points:
            if world.level.objects_of_type_at(xy, Enemy):
                return False
        return spawn_func(xy)
    return spawner


# We want to spawn near resources so they aren't too safe to simply mine out at leisure
# We spawn at a fixed rate, first near resources. If near_spawner returns false,
# we then try across the map. If it far_spawner fails, we give up for now.
class EnemySpawner:
    def __init__(self,near_spawner=spawn_if_none_within(), spawn_rate = 20, enemy_maximum=100, far_spawner=None, min_near_dist = 2, max_near_dist = 10):
        if not far_spawner: 
            far_spawner = near_spawner
        self.spawn_timer = 0
        self.min_near_dist = min_near_dist
        self.max_near_dist = max_near_dist
        self.near_spawner = near_spawner
        self.far_spawner = far_spawner
        self.enemy_maximum = enemy_maximum
        self.spawn_rate = spawn_rate

    def spawn_candidates(self, res, near):
        from globals import world
        level = world.level
        candidates = []
        for xy in make_rect( Pos(0,0), world.level.size).xy_values():
            if not level.map[xy].blocked and not any(level.objects_at(xy)):
                if not world.fov.is_visible(xy):
                    dist = min( [ xy.distance(r.xy) for r in res ] )
                    if not near or (dist >= self.min_near_dist and dist <= self.max_near_dist):
                        candidates.append(xy)
        return candidates

    def spawn_try(self, res, near):
        from globals import world
        candidates = self.spawn_candidates(res, near)
        if candidates == []:
            return False
        rand_xy = candidates[ rand(0, len(candidates)-1) ]
        if near:
            return self.near_spawner(rand_xy)
        else:
            return self.far_spawner(rand_xy)

    def spawn(self):
        from globals import world
        from resource import Resource
        # First try near resources
        res = world.level.objects_of_type(Resource)
        if not self.spawn_try(res, True):
            print "SPAWNING FAR!"
            self.spawn_try(res, False)

    def step(self):
        from globals import world
        from enemies import Enemy

        self.spawn_timer = max(0, self.spawn_timer-1)
        amount_of_enemies = len(world.level.objects_of_type(Enemy))
        if self.spawn_timer <= 0 and amount_of_enemies < self.enemy_maximum:
            self.spawn()
            self.spawn_timer = self.spawn_rate
    