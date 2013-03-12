
from gameobject import GameObject
from geometry import *
from tiles import *
import globals
import colors

APPLE = TileType(
        # ASCII mode
         { "char" : 'A', "color" : colors.PALE_RED },
        # Tile mode        
        variant_list(
            [ tile(3,2), tile(4,2), tile(3,3), tile(4,3) ], {}
        )
)

class Resource(GameObject):
    def __init__(self, xy, variant=0):
        GameObject.__init__(self, xy, APPLE, solid=True, draw_once_seen=True)
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        self.tile_variant = variant