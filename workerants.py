import colors
import libtcodpy as libtcod

from combatobject import CombatObject, CombatStats
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
WORKER_ANT_MAX_HISTORY = 30
WORKER_ANT_HISTORY_PENALTY = 30

class WorkerAnt(CombatObject):
    def __init__(self, xy):
        stats = CombatStats(
            hp = 20,
            hp_regen = 0,
            mp = 0, 
            mp_regen = 0, 
            attack = 0
        )

        CombatObject.__init__(self, xy, WORKER_ANT_TILE, stats)
        self.past_squares = [] # Weigh these lower
        self.carrying = False

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
        if obj.tile_type == resource.APPLE: 
            self.tile_type = WORKER_ANT_WITH_APPLE_TILE
        elif obj.tile_type == resource.ORANGE: 
            self.tile_type = WORKER_ANT_WITH_ORANGE_TILE
        elif obj.tile_type == resource.WATERMELON: 
            self.tile_type = WORKER_ANT_WITH_WATERMELON_TILE
        self.carrying = True

    def dropoff(self):
        from globals import world
        self.tile_type = WORKER_ANT_TILE
        world.player.add_harvest_points(10)
        self.carrying = False

    def handle_pickups_and_dropoffs(self, xy_near):
        from globals import world
        if not self.carrying:
            for xy in xy_near:
                for obj in world.level.objects_at(xy):
                    if isinstance(obj, resource.Resource) and obj.resources_left > 0:
                        self.pickup(obj)
                        return
        if self.carrying:
            for xy in xy_near:
                for obj in world.level.objects_at(xy):
                    if isinstance(obj, WorkerAntHole):
                        self.dropoff()
                        return

    def step(self):
        from globals import world
        CombatObject.step(self)
        xy_near = list( make_rect(self.xy - Pos(1,1), Size(3,3)).edge_values() )
        self.handle_pickups_and_dropoffs(xy_near)

        valid = filter(lambda xy: world.level.map.valid_xy(xy) and not world.level.is_solid(xy), xy_near)

        if valid == []: 
            return

        libtcod.random_set_distribution(0, libtcod.DISTRIBUTION_GAUSSIAN)
        weights = [ world.level.scents.trailmap[xy] + rand(-30, +30) for xy in valid]
        libtcod.random_set_distribution(0, libtcod.DISTRIBUTION_LINEAR)

        for i in range(len(weights)):
            if valid[i] in self.past_squares:
                amount = sum( filter(lambda xy: xy == valid[i], self.past_squares) )
                amount = math.sqrt(amount)
                place = self.past_squares.index(valid[i])
                if self.carrying: # Retrace our steps
                    weights[i] += WORKER_ANT_HISTORY_PENALTY*amount+ place
                else:
                    weights[i] -= WORKER_ANT_HISTORY_PENALTY*amount + place

        max_idx = weights.index(max(weights))
        self.move( valid[max_idx] )

    def die(self):
        from enemies import Corpse
        globals.world.level.queue_removal(self)
        globals.world.level.add_to_front(Corpse("Worker Ant", self.xy, self.corpse_tile, 
                                                can_be_eaten = True,
                                                mp_gain = WORKER_ANT_CANIBALISM_MP_GAIN, 
                                                hp_gain = WORKER_ANT_CANIBALISM_HP_GAIN))

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
          "color" : colors.GREEN
         }
)

class WorkerAntHole(GameObject):
    def __init__(self, xy):
        GameObject.__init__(self, xy, WORKER_ANT_HOLE, solid = False, draw_once_seen = True)
        self.spawning = False

    def start_spawning(self):
        self.spawning = True
        self.tile_type= SPAWNING_WORKER_ANT_HOLE

    def step(self):
        from globals import world

        GameObject.step(self)
        if self.spawning:
            if not world.level.solid_object_at(self.xy):
                world.level.add( WorkerAnt(self.xy) )
                self.spawning = False
                self.tile_type = WORKER_ANT_HOLE
        