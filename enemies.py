import libtcodpy as libtcod
import globals
import colors
from geometry import * 
import paths

from gameobject import GameObject
from combatobject import CombatStats, CombatObject
from tiles import *
from utils import *
import colors

class Corpse(GameObject):
    def __init__(self, xy, tiletype): 
        GameObject.__init__(self, xy, tiletype, solid=False, draw_once_seen = True)
        self.time_to_live = 10
    def step(self):
        self.time_to_live -= 1
        if self.time_to_live <= 0:
            globals.world.level.queue_removal(self)

class EnemyBehaviour:
    def __init__(self, following_steps = 0):
        self.following_steps = following_steps

class Enemy(CombatObject):
    def __init__(self, xy, tiletype, corpsetile, behaviour, stats): 
        CombatObject.__init__(self, xy, tiletype, stats)
        self.stats = stats
        self.corpse_tile = corpsetile
        self.behaviour = behaviour
        self.following_steps = 0

    def die(self):
        globals.world.level.queue_removal(self)
        globals.world.level.add_to_front(Corpse(self.xy, self.corpse_tile))
    def step(self):
        moved = False
        self.following_steps = max(0, self.following_steps - 1)
        if rand(0, 8) == 0: 
            return #Random chance of not moving

        # Move towards player
        visible = globals.world.fov.is_visible(self.xy)
        if visible or self.following_steps > 0:
            if visible: 
                self.following_steps = self.behaviour.following_steps
            # TODO: path to colony
            xy = paths.towards(self.xy, globals.world.player.xy, consider_unexplored_blocked = False, allow_digging = True)
            if xy == globals.world.player.xy:
                globals.world.player.take_damage( self.stats.attack )
                moved = True
            elif xy and not globals.world.level.solid_object_at(xy):
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
    return Enemy(xy, LADYBUG_TILE, LADYBUG_DEAD_TILE, 
                 EnemyBehaviour(following_steps = 2),
                 CombatStats(hp = 20, hp_regen = 0, mp = 0, mp_regen = 0, attack = 5))