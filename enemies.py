import libtcodpy as libtcod
import globals
import colors
from geometry import * 
import paths

from gameobject import GameObject
from tiles import *
from utils import *
import colors

class Corpse(GameObject):
    def __init__(self, xy, tiletype): 
        GameObject.__init__(self, xy, tiletype)
        self.time_to_live = 10
    def step(self):
        self.time_to_live -= 1
        if self.time_to_live <= 0:
            globals.world.level.queue_removal(self)


class EnemyStats:
    def __init__(self, hp, attack):
        self.hp = hp
        self.attack = attack

class Enemy(GameObject):
    def __init__(self, xy, tiletype, corpsetile, stats): 
        GameObject.__init__(self, xy, tiletype)
        self.stats = stats
        self.corpse_tile = corpsetile
    def step(self):
        moved = False
        if rand(0, 8) == 0: 
            return #Random chance of not moving

        # Move towards player
        if globals.world.fov.is_visible(self.xy):
            # TODO: path to colony
            xy = paths.towards(self.xy, globals.world.player.xy, consider_unexplored_blocked = False, allow_digging = True)
            if xy and not globals.world.level.solid_object_at(xy):
                map = globals.world.level.map
                if map[xy].type == DIGGABLE:
                    # Swap tiles when digging through
                    map[xy], map[self.xy] = map[self.xy], map[xy]
                self.xy = xy
                moved = True

        # Wander
        if not moved:
            level = globals.world.level
            xy = random_nearby(level, self.xy, lambda xy: not level.is_solid(xy) )
            if xy:
                self.xy = xy
                moved = True

    def draw(self):
        GameObject.draw(self)
    def take_damage(self, damage):
        self.stats.hp = max(0, self.stats.hp - damage)
        if self.stats.hp <= 0:
            self.die()
    def die(self):
        globals.world.level.queue_removal(self)
        globals.world.level.add_to_front(Corpse(self.xy, self.corpse_tile))

LADYBUG_TILE = TileType(    # ASCII mode
         { "char" : 'l', 
           "color" : colors.RED
         },                 # Tile mode
         { "char" : tile(2,0)
         }
)

LADYBUG_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.RED
         },                     # Tile mode
         { "char" : tile(2,6)
         }
)
def ladybug(xy):
    return Enemy(xy, LADYBUG_TILE, LADYBUG_DEAD_TILE, EnemyStats(20,5))