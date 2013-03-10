import libtcodpy as libtcod
from actions import *
import globals
import colors
from geometry import * 
import paths

from gameobject import GameObject
from tiles import TileType, tile

STAIRS_DOWN = TileType(  # ASCII mode
         { "char" : '>', 
           "color" : colors.YELLOW
         },              # Tile mode
         { "char" : '>', 
           "color" : colors.YELLOW
         }
)

STAIRS_UP = TileType(    # ASCII mode
         { "char" : '<', 
           "color" : colors.YELLOW
         },              # Tile mode
         { "char" : '<', 
           "color" : colors.YELLOW
         }
)

class Stairs(GameObject):
    def __init__(self, xy, stairs_down): 
        print "Created at ", xy
        GameObject.__init__(self, xy, STAIRS_DOWN if stairs_down else STAIRS_UP, draw_once_seen = True)
        self.stairs_down = stairs_down
