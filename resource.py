
from gameobject import GameObject
from geometry import *
from tiles import *
import colors

PEACH = TileType(
        # ASCII mode
         { "char" : 'P', "color" : colors.YELLOW },
        # Tile mode
         { "char" : tile(0,2) }
)

class Resource(GameObject):
    def __init__(self, xy):
        GameObject.__init__(self, xy, PEACH)
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)