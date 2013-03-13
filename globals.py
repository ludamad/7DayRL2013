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

effects = console.Console(SCREEN_SIZE)
effects.set_default_background(colors.BLACK)

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

    game_blit(True)

def game_blit(flush):
    con.blit( make_rect(Pos(0,0), SCREEN_SIZE), screen )
    panel.blit( make_rect( Pos(0,0), panel.size), screen, Pos(0, SCREEN_SIZE.h))
    if flush:
        screen.flush()

def key2direction(key):
    if key.vk == libtcod.KEY_UP or key.c == ord('k') or key.vk == libtcod.KEY_KP8 or key.c == ord('8'):
        return ( 0, -1 )
    elif key.vk == libtcod.KEY_DOWN or key.c == ord('j') or key.vk == libtcod.KEY_KP2 or key.c == ord('2'):
        return ( 0, +1 )
    elif key.vk == libtcod.KEY_LEFT or key.c == ord('h') or key.vk == libtcod.KEY_KP4 or key.c == ord('4'):
        return ( -1, 0 )
    elif key.vk == libtcod.KEY_RIGHT or key.c == ord('l') or key.vk == libtcod.KEY_KP6 or key.c == ord('6'):
        return ( +1, 0 )
    elif key.c == ord('b') or key.vk == libtcod.KEY_KP1 or key.c == ord('1'):
        return ( -1, +1 )
    elif key.c == ord('n') or key.vk == libtcod.KEY_KP3 or key.c == ord('3'):
        return ( +1, +1 )
    elif key.c == ord('y') or key.vk == libtcod.KEY_KP7 or key.c == ord('7'):
        return ( -1, -1 )
    elif key.c == ord('u') or key.vk == libtcod.KEY_KP9 or key.c == ord('9'):
        return ( +1, -1 )
    elif key.vk == libtcod.KEY_SPACE or key.c == ord('.') or key.vk == libtcod.KEY_KP5 or key.c == ord('5'):
        return ( 0, 0 )
    return None