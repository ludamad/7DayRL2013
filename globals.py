import dungeon
from geometry import *
import libtcodpy as libtcod
import console
import colors

VIEW_PADDING = 10
SCREEN_SIZE = Size(80, 50)
LEVEL_SIZE = SCREEN_SIZE

world = dungeon.World()

con = console.Console(SCREEN_SIZE)
con.set_default_background(colors.BLACK)
con.clear()

ASCII_MODE = False

panel = console.Console( Size(SCREEN_SIZE.w, 7) )

def on_screen(xy):
    return xy - world.view.top_left()