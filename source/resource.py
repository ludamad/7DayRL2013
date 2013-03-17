
from gameobject import GameObject
from geometry import *
from tiles import *
import globals
import colors

APPLE = TileType(
        # ASCII mode
         { "char" : 247, "color" : colors.PALE_RED },
        # Tile mode        
        variant_list(
            [ tile(3,2), tile(4,2), tile(3,3), tile(4,3) ], {}
        )
)

ORANGE = TileType(
        # ASCII mode
         { "char" : 247, "color" : colors.ORANGE },
        # Tile mode
        variant_list(
            [ tile(5,2), tile(6,2), tile(5,3), tile(6,3) ], {}
        )
)

WATERMELON = TileType(
        # ASCII mode
         { "char" : 247, "color" : colors.Color(232,34,62) },
        # Tile mode
        variant_list(
            [ tile(3,4), tile(4,4), tile(3,5), tile(4,5) ], {}
        )
)

class Resource(GameObject):
    def __init__(self, xy, name, type, variant=0, resources_left=1):
        GameObject.__init__(self, xy, type, solid=True, draw_once_seen=True)
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        self.tile_variant = variant
        self.name = name
        self.resources_left = resources_left
        self.seen = False
    def apply_scent(self, scents):
        scents.apply_scent_towards(self.xy, 70, radius=4)
    # Takes a resource, returns false if all have already been taken
    def take(self):
        from globals import world
        if self.resources_left <= 0:
            return False
        self.resources_left -= 1
        if self.resources_left <= 0:
            world.level.queue_removal(self)
        return True

    def step(self):
        GameObject.step(self)
        if not self.seen and globals.world.fov.is_visible(self.xy):
            globals.world.messages.add([colors.ORANGE, "You find " + self.name + "!"])
            self.seen = True

DROPPED_APPLE = TileType({ "char" : 247, "color" : colors.PALE_RED }, { "char" : tile(9,7) } )
DROPPED_ORANGE = TileType({ "char" : 247, "color" : colors.ORANGE }, { "char" : tile(10,7) } )
DROPPED_WATERMELON =  TileType({ "char" : 247, "color" : colors.Color(232,34,62) }, { "char" : tile(11,7) } )

def drop_resource(xy, tile):
    from globals import world
    from workerants import WORKER_ANT_WITH_APPLE_TILE, WORKER_ANT_WITH_ORANGE_TILE, WORKER_ANT_WITH_WATERMELON_TILE
    if tile == WORKER_ANT_WITH_APPLE_TILE:
        res = Resource(xy, "an apple", DROPPED_APPLE, resources_left=1)
    elif tile == WORKER_ANT_WITH_ORANGE_TILE:
        res = Resource(xy, "an orange", DROPPED_ORANGE, resources_left=1)
    elif tile == WORKER_ANT_WITH_WATERMELON_TILE:
        res = Resource(xy, "some watermelon", DROPPED_WATERMELON, resources_left=1)
    world.level.add(res)

def apple(xy, variant):
    return Resource(xy, "an apple", APPLE, variant)

def orange(xy, variant):
    return Resource(xy, "an orange", ORANGE, variant)

def watermelon(xy, variant):
    return Resource(xy, "some watermelon", WATERMELON, variant)
