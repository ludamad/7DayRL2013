import libtcodpy as libtcod
import globals
import colors
from geometry import * 
import paths

from gameobject import GameObject
from combatobject import CombatStats, CombatObject, TEAM_ENEMY, TEAM_PLAYER
from tiles import *
from utils import *
import colors

class Corpse(GameObject):
    def __init__(self, name, xy, tiletype, can_be_eaten=True, hp_gain=0, mp_gain=0):
        GameObject.__init__(self, xy, tiletype, solid=False, draw_once_seen = False)
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
                if not world.level.is_alive(obj):
                    continue
                obj.stats.regen_hp(self.hp_gain)
                obj.stats.regen_mp(self.mp_gain)
                if obj == globals.world.player:
                    msg = [colors.GREEN, 'You consume the ' + self.name + ", gaining " + str(self.hp_gain) + " HP"]
                    msg[1] += ", " + str(self.mp_gain) + " MP." if self.mp_gain > 0 else "."
                else:
                    msg = [colors.GRAY, 'The '+ obj.name +' consumes the ' + self.name + "!"]
                world.messages.add( msg )
                globals.world.level.queue_removal(self)
                return
        if self.time_to_live <= 0:
            globals.world.level.queue_removal(self)

class EnemyBehaviour:
    def __init__(self, corpse_heal=0, corpse_mana=0, attack_range=1, can_fly=False, can_burrow = True, wander_burrow_chance = 0.0, following_steps = 0, sight_distance=8, pause_chance = 1.0/8):
        self.following_steps = following_steps
        self.can_burrow = can_burrow
        self.attack_range = attack_range
        self.wander_burrow_chance = wander_burrow_chance
        self.corpse_heal = corpse_heal
        self.corpse_mana = corpse_mana
        self.can_fly = can_fly
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
        self.following_object = None

    def apply_scent(self, scents):
        scents.apply_scent_towards(self.xy, -25)

    def die(self):
        if not globals.world.level.is_alive(self):
            return
        globals.world.level.queue_removal(self)
        corpse = Corpse(
            self.name, self.xy, self.corpse_tile, 
            can_be_eaten = True, 
            mp_gain = self.behaviour.corpse_mana, 
            hp_gain = self.behaviour.corpse_heal
        )
        globals.world.level.add_to_front_of_combatobjects(corpse)

    def move(self, xy):
        if not globals.world.level.is_alive(self):
            return
        map = globals.world.level.map
        if not self.behaviour.can_fly and map[xy].type == DIGGABLE:
            # Swap tiles when digging through
            map[xy].swap(map[self.xy])
        self.xy = xy

    def _line_to(self, obj):
        map = globals.world.level.map
        for x, y in libtcod.line_iter(self.xy.x, self.xy.y, obj.xy.x, obj.xy.y):
            if map[Pos(x,y)].blocked:
                return False
        return True
    def _is_target_visible(self, obj, allow_follow=True):
        if allow_follow and self.following_object == obj:
            return True
        if obj.xy.distance(self.xy) > self.behaviour.sight_distance:
            return False
        if self.behaviour.can_fly:
            return True
        if obj == globals.world.player:
            return globals.world.fov.is_visible(self.xy)
        return self._line_to(obj)

    def _find_target(self):
        from globals import world
        mindist = self.behaviour.sight_distance+1
        minobj = None
        for obj in world.level.objects:
            if not isinstance(obj, CombatObject): continue
            if obj.team == self.team: continue
            if not self._is_target_visible(self, obj): continue

            dist = obj.xy.distance(self.xy)
            if dist < mindist:
                mindist = dist
                minobj = obj
        return minobj

    def _try_to_attack(self, target):
        diff = self.xy - target.xy
        sqr_dist = max(abs(diff.x), abs(diff.y))
        if sqr_dist > self.behaviour.attack_range:
            return False
        if self.behaviour.attack_range == 1 or self._line_to(target):
            self.attack(target)
            return True
        return False

    def step(self):
        from globals import world

        CombatObject.step(self)

        moved = False
        self.following_steps = max(0, self.following_steps - 1)
        if self.following_steps == 0:
            self.following_object = None

        if rand(0, 100)/100.0 < self.behaviour.pause_chance: 
            return #Random chance of not moving

        # Move towards hostile CombatObject (different 'team', enemies can be player-aligned due to spells)
        target = self._find_target()
        if target:
            if self._is_target_visible(target, False):
                self.following_steps = self.behaviour.following_steps
                self.following_object = target
                if self._try_to_attack(target):
                    moved = True
                else:
                    xy = paths.towards(self.xy, target.xy, avoid_solid_objects = True, consider_unexplored_blocked = False, allow_digging = self.behaviour.can_burrow)
                    if xy:
                        self.move(xy)
                        moved = True

        # Wander
        if not moved:
            level = globals.world.level
            can_wander_burrow = (rand(0,999)/1000.0 <= self.behaviour.wander_burrow_chance)
            criteria = lambda sxy: not level.is_solid(sxy) or (can_wander_burrow and level.map[sxy].type == DIGGABLE)
            xy = random_nearby(level, self.xy, criteria)
            if xy:
                self.move(xy)
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
                    wander_burrow_chance = 0.01,
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
                    wander_burrow_chance = 0.5,
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
           "color" : colors.ORANGE
         },                 # Tile mode
         { "char" : tile(4,0)
         }
)

ROACH_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.ORANGE
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
                    wander_burrow_chance = 0.1,
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
                    wander_burrow_chance = 0.02,
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

SCORPION_TILE = TileType(
         { "char" : 's', "color" : colors.Color(150,61,41) }, # ASCII mode              
         { "char" : tile(0,7) } # Tile mode
)
SCORPION_DEAD_TILE = TileType(
         { "char" : '%', "color" : colors.Color(150,61,41) }, # ASCII mode              
         { "char" : tile(0,8) } # Tile mode
)
def scorpion(xy):
    return Enemy(
             "Scorpion",
             xy,
             SCORPION_TILE, 
             SCORPION_DEAD_TILE, 
             EnemyBehaviour(
                    corpse_heal = 20,
                    corpse_mana = 10,
                    attack_range = 2,
                    can_burrow = True,
                    wander_burrow_chance = 0.02,
                    following_steps = 2,
                    pause_chance = 0.25,
                    sight_distance = 5.3
             ),
             CombatStats(
                    hp = 20,
                    hp_regen = 0,
                    mp = 0, 
                    mp_regen = 0, 
                    attack = 5
            )
    )