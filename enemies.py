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
    def __init__(self, name, xy, tiletype, can_be_eaten=True, hp_gain=0):
        GameObject.__init__(self, xy, tiletype, solid=False, draw_once_seen = True)
        self.name = name
        self.time_to_live = 10
        self.can_be_eaten = can_be_eaten
        self.hp_gain = hp_gain
    def step(self):
        from globals import world
    
        self.time_to_live -= 1
        for obj in globals.world.level.objects_at(self.xy):
            if isinstance(obj, CombatObject):
                obj.stats.regen_hp(self.hp_gain)
                world.messages.add( [colors.GREEN, 'You consume the ' + self.name + ", healing " + str(self.hp_gain) + " HP."] )
                globals.world.level.queue_removal(self)
                return
        if self.time_to_live <= 0:
            globals.world.level.queue_removal(self)

class EnemyBehaviour:
    def __init__(self, corpse_heal=0, can_burrow = True, following_steps = 0, pause_chance = 1.0/8):
        self.following_steps = following_steps
        self.can_burrow = can_burrow
        self.corpse_heal = corpse_heal
        self.pause_chance = pause_chance

class Enemy(CombatObject):
    def __init__(self, name, xy, tiletype, corpsetile, behaviour, stats): 
        CombatObject.__init__(self, xy, tiletype, stats)
        self.name = name
        self.stats = stats
        self.corpse_tile = corpsetile
        self.behaviour = behaviour
        self.following_steps = 0

    def take_damage(self, attacker, damage):
        from globals import world
        CombatObject.take_damage(self, attacker, damage)
        world.messages.add( [colors.BABY_BLUE, 'You bite the ' + self.name + " for " + str(int(damage)) + ' damage!'] )

    def die(self):
        globals.world.level.queue_removal(self)
        globals.world.level.add_to_front(Corpse(self.name, self.xy, self.corpse_tile, can_be_eaten = True, hp_gain = self.behaviour.corpse_heal))
    def step(self):
        moved = False
        self.following_steps = max(0, self.following_steps - 1)
        if rand(0, 100)/100.0 < self.behaviour.pause_chance: 
            return #Random chance of not moving

        # Move towards player
        visible = globals.world.fov.is_visible(self.xy)
        if visible or self.following_steps > 0:
            if visible: 
                self.following_steps = self.behaviour.following_steps
            # TODO: path to colony
            xy = paths.towards(self.xy, globals.world.player.xy, consider_unexplored_blocked = False, allow_digging = self.behaviour.can_burrow)
            if xy == globals.world.player.xy:
                self.attack(globals.world.player)
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
    return Enemy(
             "Ladybug", 
             xy, 
             LADYBUG_TILE, 
             LADYBUG_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 10, 
                    can_burrow = False, 
                    following_steps = 2,
                    pause_chance = 1/8.0
             ),
             CombatStats(
                    hp = 20, 
                    hp_regen = 0, 
                    mp = 0, 
                    mp_regen = 0, 
                    attack = 5
            )
    )

ANT_TILE = TileType(    # ASCII mode
         { "char" : 'a',
           "color" : colors.PURPLE
         },                 # Tile mode
         { "char" : tile(0,0)
         }
)

ANT_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.PURPLE
         },                     # Tile mode
         { "char" : tile(0,6)
         }
)
def ant(xy):
    return Enemy(
             "Ant",
             xy, 
             ANT_TILE, 
             ANT_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 5,
                    can_burrow = True, 
                    following_steps = 2,
                    pause_chance = 0.0
             ),
             CombatStats(
                    hp = 10,
                    hp_regen = 0,
                    mp = 0, 
                    mp_regen = 0, 
                    attack = 5
            )
    )