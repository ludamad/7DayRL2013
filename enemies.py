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
    def __init__(self, name, xy, tiletype, can_be_eaten=True, hp_gain=0, mp_gain=0):
        GameObject.__init__(self, xy, tiletype, solid=False, draw_once_seen = True)
        self.name = name
        self.time_to_live = 10
        self.can_be_eaten = can_be_eaten
        self.hp_gain = hp_gain
        self.mp_gain = mp_gain
    def step(self):
        from globals import world
    
        self.time_to_live -= 1
        for obj in globals.world.level.objects_at(self.xy):
            if isinstance(obj, CombatObject):
                obj.stats.regen_hp(self.hp_gain)
                obj.stats.regen_mp(self.mp_gain)
                msg = [colors.GREEN, 'You consume the ' + self.name + ", gaining " + str(self.hp_gain) + " HP"]
                msg[1] += ", " + str(self.mp_gain) + " MP." if self.mp_gain > 0 else "."
                world.messages.add( msg )
                globals.world.level.queue_removal(self)
                return
        if self.time_to_live <= 0:
            globals.world.level.queue_removal(self)

class EnemyBehaviour:
    def __init__(self, corpse_heal=0, corpse_mana=0, can_burrow = True, following_steps = 0, sight_distance=8, see_through_walls=False, pause_chance = 1.0/8):
        self.following_steps = following_steps
        self.can_burrow = can_burrow
        self.corpse_heal = corpse_heal
        self.corpse_mana = corpse_mana
        self.see_through_walls = see_through_walls
        self.sight_distance = sight_distance
        self.pause_chance = pause_chance

class Enemy(CombatObject):
    def __init__(self, name, xy, tiletype, corpsetile, behaviour, stats): 
        CombatObject.__init__(self, xy, tiletype, stats)
        self.name = name
        self.stats = stats
        self.corpse_tile = corpsetile
        self.behaviour = behaviour
        self.following_steps = 0

    def die(self):
        globals.world.level.queue_removal(self)
        corpse = Corpse(
            self.name, self.xy, self.corpse_tile, 
            can_be_eaten = True, 
            mp_gain = self.behaviour.corpse_mana, 
            hp_gain = self.behaviour.corpse_heal
        )
        globals.world.level.add_to_front_of_combatobjects(corpse)
    def step(self):
        CombatObject.step(self)

        moved = False
        self.following_steps = max(0, self.following_steps - 1)
        if rand(0, 100)/100.0 < self.behaviour.pause_chance: 
            return #Random chance of not moving

        # Move towards player
        visible = globals.world.player.xy.distance(self.xy) <= self.behaviour.sight_distance
        visible = visible and (self.behaviour.see_through_walls or globals.world.fov.is_visible(self.xy))
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
                    corpse_heal = 8,
                    corpse_mana = 2, 
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
           "color" : colors.RED
         },                 # Tile mode
         { "char" : tile(1,0)
         }
)

ANT_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.RED
         },                     # Tile mode
         { "char" : tile(1,6)
         }
)

def ant(xy):
    return Enemy(
             "Ant",
             xy, 
             ANT_TILE, 
             ANT_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 4,
                    corpse_mana = 1,
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


ROACH_TILE = TileType(    # ASCII mode
         { "char" : 'r',
           "color" : colors.PINKISH
         },                 # Tile mode
         { "char" : tile(4,0)
         }
)

ROACH_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.PINKISH
         },                     # Tile mode
         { "char" : tile(4,6)
         }
)
def roach(xy):
    return Enemy(
             "Roach",
             xy,
             ROACH_TILE, 
             ROACH_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 16,
                    corpse_mana = 4,
                    can_burrow = True,
                    following_steps = 1,
                    pause_chance = 0.25,
                    sight_distance = 3.3
             ),
             CombatStats(
                    hp = 20,
                    hp_regen = 0,
                    mp = 0, 
                    mp_regen = 0, 
                    attack = 10
            )
    )

BEETLE_TILE = TileType(    # ASCII mode
         { "char" : 'B',
           "color" : colors.Color(123,57,59)
         },                 # Tile mode
         { "char" : tile(3,7)
         }
)

BEETLE_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.Color(123,57,59)
         },                     # Tile mode
         { "char" : tile(3,8)
         }
)
def beetle(xy):
    return Enemy(
             "Beetle",
             xy,
             BEETLE_TILE, 
             BEETLE_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 25,
                    corpse_mana = 10,
                    can_burrow = True,
                    following_steps = 2,
                    pause_chance = 0.25,
                    sight_distance = 5.3
             ),
             CombatStats(
                    hp = 50,
                    hp_regen = 0,
                    mp = 0, 
                    mp_regen = 0, 
                    attack = 20
            )
    )