import colors
import libtcodpy as libtcod

from combatobject import CombatObject, CombatStats, TEAM_PLAYER
from gameobject import GameObject

import resource
from geometry import *
from utils import *
from tiles import *

WORKER_ANT_TILE = TileType(    
         { "char" : 'a', "color" : colors.PURPLE }, # ASCII mode
         { "char" : tile(0,0) }  # Tile mode
)
_CARRYING_ASCII = { "char" : 'a', "color" : colors.GREEN }

WORKER_ANT_WITH_APPLE_TILE      = TileType(_CARRYING_ASCII, { "char" : tile(4,7) } )
WORKER_ANT_WITH_ORANGE_TILE     = TileType(_CARRYING_ASCII, { "char" : tile(5,7) } )
WORKER_ANT_WITH_WATERMELON_TILE = TileType(_CARRYING_ASCII, { "char" : tile(6,7) } )

WORKER_ANT_DEAD_TILE = TileType(
         { "char" : '%',  "color" : colors.PURPLE }, # ASCII mode
         { "char" : tile(0,6) } # Tile mode
)

WORKER_ANT_CANIBALISM_HP_GAIN = 4
WORKER_ANT_CANIBALISM_MP_GAIN = 1
WORKER_ANT_MAX_HISTORY = 20
WORKER_ANT_HISTORY_PENALTY = 30
WORKER_ANT_TURNS_BEFORE_BURROW = 100

class WorkerAnt(CombatObject):
    def __init__(self, xy):
        stats = CombatStats(
            hp = 20,
            hp_regen = 0,
            mp = 0, 
            mp_regen = 0, 
            attack = 0
        )

        CombatObject.__init__(self, xy, WORKER_ANT_TILE, stats, team = TEAM_PLAYER)
        self.past_squares = [] # Weigh these lower
        self.carrying = False
        self.name = "Worker Ant"
        self.turns = 0
        self.corpse_tile = WORKER_ANT_DEAD_TILE

    def take_damage(self, attacker, damage):
        from globals import world
        from enemies import Enemy

        CombatObject.take_damage(self, attacker, damage)
        if isinstance(attacker, Enemy):
            world.messages.add( [colors.RED, 'The ' + attacker.name + ' bites your worker ant for ' + str(int(damage)) + ' damage!'] )

    def move(self, xy):
        self.trail()

        # Add to location history
        if not self.carrying:
            # Update location in history if exists
            self.past_squares.append(xy)
            if len(self.past_squares) > WORKER_ANT_MAX_HISTORY:
                del self.past_squares[0 : len(self.past_squares) - WORKER_ANT_MAX_HISTORY]
        self.xy = xy

    def pickup(self, obj):
        if not obj.take(): return
        self.trail()
        if obj.tile_type == resource.APPLE or resource.DROPPED_APPLE: 
            self.tile_type = WORKER_ANT_WITH_APPLE_TILE
        elif obj.tile_type == resource.ORANGE or resource.DROPPED_ORANGE: 
            self.tile_type = WORKER_ANT_WITH_ORANGE_TILE
        elif obj.tile_type == resource.WATERMELON or resource.DROPPED_WATERMELON: 
            self.tile_type = WORKER_ANT_WITH_WATERMELON_TILE
        self.carrying = True

    def back2hole(self):
        from globals import world
        if self.carrying:
            self.tile_type = WORKER_ANT_TILE
            world.player.add_harvest_points(10)
            world.messages.add([colors.BABY_BLUE, "Your worker ant delivers some harvest!"])
        else:
            world.messages.add([colors.GRAY, "Your tired ant returns to the anthole."])
        world.level.queue_removal(self)
 

    def handle_pickups_and_returns(self, xy_near):
        from globals import world
        if not self.carrying:
            for xy in xy_near:
                for obj in world.level.objects_at(xy):
                    if isinstance(obj, resource.Resource) and obj.resources_left > 0:
                        self.pickup(obj)
                        return
        if self.carrying or self.turns >= WORKER_ANT_TURNS_BEFORE_BURROW:
            for xy in xy_near:
                for obj in world.level.objects_at(xy):
                    if isinstance(obj, WorkerAntHole):
                        self.back2hole()
                        return

    def step(self):
        from globals import world
        CombatObject.step(self)
        self.turns += 1
        xy_near = list( make_rect(self.xy - Pos(1,1), Size(3,3)).edge_values() )
        self.handle_pickups_and_returns(xy_near)

        valid = filter(lambda xy: world.level.map.valid_xy(xy) and not world.level.is_solid(xy), xy_near)

        if valid == []: 
            return

        libtcod.random_set_distribution(0, libtcod.DISTRIBUTION_GAUSSIAN)
        randomness = 30
        weights = [ world.level.scents.trailmap[xy] + rand(-randomness, +randomness) for xy in valid]
        libtcod.random_set_distribution(0, libtcod.DISTRIBUTION_LINEAR)

        for i in range(len(weights)):
            if valid[i] in self.past_squares:
                amount = len( filter(lambda xy: xy == valid[i], self.past_squares) )
                bonus = 0 if amount <= 1 else 10
                if self.carrying: # Retrace our steps
                    weights[i] += WORKER_ANT_HISTORY_PENALTY + bonus
                else:
                    weights[i] -= WORKER_ANT_HISTORY_PENALTY + bonus

        max_idx = weights.index(max(weights))
        self.move( valid[max_idx] )

    def die(self):
        from globals import world
        from enemies import Corpse
        world.level.queue_removal(self)
        world.player.take_damage(self, 15)
        world.level.add_to_front_of_combatobjects(Corpse("Worker Ant", self.xy, self.corpse_tile, 
                                    can_be_eaten = True,
                                    mp_gain = WORKER_ANT_CANIBALISM_MP_GAIN, 
                                    hp_gain = WORKER_ANT_CANIBALISM_HP_GAIN))
        if self.carrying:
            resource.drop_resource(self.xy, self.tile_type)

WORKER_ANT_HOLE = TileType(    # ASCII mode
         { "char" : 'O', 
           "color" : colors.YELLOW
         },                     # Tile mode
         { "char" : tile(2,1)
         }
)

SPAWNING_WORKER_ANT_HOLE = TileType(    # ASCII mode
         { "char" : 'O', 
           "color" : colors.GREEN
         },                     # Tile mode
         { "char" : tile(2,1),
          "color" : colors.PALE_GREEN
         }
)

class WorkerAntHole(GameObject):
    def __init__(self, xy):
        GameObject.__init__(self, xy, WORKER_ANT_HOLE, solid = False, draw_once_seen = True)
        self.spawning = False
        self.spawns_left = 0
        self.spawns_timer = 0

    def start_spawning(self):
        self.spawning = True
        self.spawns_left = 4
        self.spawns_timer = 5
        self.tile_type= SPAWNING_WORKER_ANT_HOLE

    def step(self):
        from globals import world

        GameObject.step(self)
        if self.spawning:
            self.spawns_timer = max(0, self.spawns_timer - 1)
            if self.spawns_timer <= 0 and not world.level.solid_object_at(self.xy):
                # 'add_to_back_of_corpses' is a hack, but oh well
                world.level.add_to_back_of_corpses( WorkerAnt(self.xy) )
                self.spawns_left -= 1
                if self.spawns_left <= 0:
                    self.spawning = False
                    self.tile_type = WORKER_ANT_HOLE
                else:
                    self.spawns_timer = 5

