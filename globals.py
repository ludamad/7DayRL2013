import dungeon
from geometry import *
import libtcodpy as libtcod
import console
import colors

VIEW_PADDING = 10
SCREEN_SIZE = Size(80, 43)
LEVEL_SIZE = SCREEN_SIZE
RESOURCES_NEEDED = 100

world = dungeon.World()

con = console.Console(SCREEN_SIZE)
con.set_default_background(colors.BLACK)
con.clear()

screen = console.Console()
screen.set_default_foreground(colors.WHITE)

ASCII_MODE = False

panel = console.Console( Size(SCREEN_SIZE.w, 7) )

def on_screen(xy):
    return xy - world.view.top_left()

def game_draw():
    # Draw the level to the buffer
    panel.set_default_background(colors.BLACK)
    panel.clear()
    world.draw()
    world.player.print_stats()

    # Blit it to the screen
    con.blit( make_rect(Pos(0,0), SCREEN_SIZE), screen )
    panel.blit( make_rect( Pos(0,0), panel.size), screen, Pos(0, SCREEN_SIZE.h))
    screen.flush()

