import dungeon
from geometry import *
import libtcodpy as libtcod
import console
import colors

VIEW_PADDING = 10
SCREEN_SIZE = Size(80, 35)
LEVEL_SIZE = SCREEN_SIZE

world = dungeon.World()

con = console.Console(SCREEN_SIZE)
con.set_default_background(colors.BLACK)
con.clear()

effects = console.Console(SCREEN_SIZE)
effects.set_default_background(colors.BLACK)

screen = console.Console()
screen.set_default_foreground(colors.WHITE)

INTRO_IMAGE = libtcod.image_load("intro.png")
DEFEAT_IMAGE = libtcod.image_load("defeat.png")
VICTORY_IMAGE = libtcod.image_load("victory.png")

def splash_screen(img=None):
    from utils import print_colored
    from menus import menu, msgbox
    from tiles import tile
    screen.clear()

    while True:
        if img:
            screen.clear()
            libtcod.image_blit_rect(img, 0, 0,0, -1,-1, 1)
            if img == INTRO_IMAGE:
                print_colored(screen, Pos(30, 30), colors.WHITE, "PRESS ENTER TO START!")
            screen.flush()
        else:
            game_draw()
        key, mouse = libtcod.Key(), libtcod.Mouse()
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
        if key.pressed and key.vk == libtcod.KEY_ENTER:
            if img == INTRO_IMAGE:
                opt = menu((colors.WHITE, "Select a mode (changeable in-game with 'tab'):"), 
                            [(colors.PALE_RED, "Tiles mode"),(colors.PALE_GREEN, "Classic ASCII") ], 50, index_color=colors.YELLOW)
                global ASCII_MODE
                ASCII_MODE = (opt == 1)
                if opt != None: 
                    hole= [] if not ASCII_MODE else [colors.YELLOW, ' (O)']
                    explanation = [ colors.BABY_BLUE, "Welcome to BUGHACK\n",
                                    colors.WHITE, "You are a leader ant who must lead worker ants to delicious harvest.\n",
                                    colors.WHITE, "Every sector you must gather a certain amount of harvest.\n", 
                                    colors.PALE_RED, "Keep your ants safe, or you'll take damage!\n", 
                                    colors.WHITE, "You must call ants out of an ant hole"] + hole + [colors.WHITE,", and then lead them to \n",
                                    colors.WHITE, "to fruit.\n",colors.WHITE, '\n',
                                    colors.YELLOW, "Press C in-game to see controls."]
                    screen.clear()
                    libtcod.image_blit_rect(img, 0, 0,0, -1,-1, 1)
                    screen.flush()
                    msgbox(explanation, 70)
                    if game_save_exists():
                        game_load()
                else:
                    continue
            screen.clear()
            screen.flush()
            return
        elif (key.pressed and key.vk == libtcod.KEY_ESCAPE) or libtcod.console_is_window_closed():
            exit()

ASCII_MODE = False

panel = console.Console( Size(SCREEN_SIZE.w, 7) )

def on_screen(xy):
    return xy - world.view.top_left()

def game_draw(fulldraw=False):
    from statuses import SUGAR_RUSH, DEFENCE
    # Draw the level to the buffer
    panel.set_default_background(colors.BLACK)
    if world.player.has_status(SUGAR_RUSH):
        panel.set_default_background(colors.DARK_RED)
    elif world.player.has_status(DEFENCE):
        panel.set_default_background(colors.DARKER_GRAY)
    panel.clear()
    world.draw(fulldraw)
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

def game_save_exists():
    return False
    try: 
        f = open("gamesave.save")
        f.close()
        return True
    except IOError:
        return False

def game_load():
    from pickle import load
    world = load("gamesave.save")
    world.step()
    game_draw(True)

def game_save_delete():
    pass

def game_save_and_exit():    
#    from pickle import dump
#    dump(world, open("gamesave.save", "w"))
    exit()
