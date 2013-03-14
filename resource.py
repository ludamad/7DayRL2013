
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
    def __init__(self, xy, name, type, variant=0):
        GameObject.__init__(self, xy, type, solid=True, draw_once_seen=True)
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        self.tile_variant = variant
        self.name = name
        self.resources_left = 3
        self.seen = False
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

def apple(xy, variant):
    return Resource(xy, "an apple", APPLE, variant)

def orange(xy, variant):
    return Resource(xy, "an orange", ORANGE, variant)

def watermelon(xy, variant):
    return Resource(xy, "some watermelon", WATERMELON, variant)
