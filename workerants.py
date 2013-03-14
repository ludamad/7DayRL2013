import colors

from combatobject import CombatObject, CombatStats
from gameobject import GameObject

from geometry import *
from utils import *
from tiles import *

WORKER_ANT_TILE = TileType(    # ASCII mode
         { "char" : 'a',
           "color" : colors.PURPLE
         },                 # Tile mode
         { "char" : tile(0,0)
         }
)

WORKER_ANT_DEAD_TILE = TileType(    # ASCII mode
         { "char" : '%', 
           "color" : colors.PURPLE
         },                     # Tile mode
         { "char" : tile(0,6)
         }
)

WORKER_ANT_CANIBALISM_HP_GAIN = 4
WORKER_ANT_CANIBALISM_MP_GAIN = 1
WORKER_ANT_MAX_HISTORY = 5
WORKER_ANT_HISTORY_PENALTY = 20

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

    def move(self, xy):
        self.trail()
        self.past_squares.append(xy)
        if len(self.past_squares) > WORKER_ANT_MAX_HISTORY:
            del self.past_squares[0 : len(self.past_squares) - WORKER_ANT_MAX_HISTORY]
        self.xy = xy

    def step(self):
        from globals import world
        CombatObject.step(self)
        xy_near = make_rect(self.xy - Pos(1,1), Size(3,3)).edge_values()
        valid = filter(lambda xy: world.level.map.valid_xy(xy) and not world.level.is_solid(xy), xy_near)

        if valid == []: 
            return

        weights = [ world.level.scents.trailmap[xy] + rand(0,10) for xy in valid]

        for i in range(len(weights)):
            if valid[i] in self.past_squares:
                weights[i] -= WORKER_ANT_HISTORY_PENALTY

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
        