import libtcodpy as libtcod
from geometry import *
import console

screen = console.Console()

def menu(header, options, width):
    from globals import SCREEN_SIZE

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
 
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = screen.get_height_rect( Rect(0, 0, width, SCREEN_SIZE.h), header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
 
    #create an off-screen console that represents the menu's window
    window = console.Console( Size(width, height) )
 
    #print the header, with auto-wrap
    window.set_default_foreground(libtcod.white)
    window.print_rect_ex(Rect(0, 0, width, height), libtcod.BKGND_NONE, libtcod.LEFT, header)
 
    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        window.print_ex(window, Pos(0, y), libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
 
    #blit the contents of "window" to the root console
    x = SCREEN_SIZE.w/2 - width/2
    y = SCREEN_SIZE.h/2 - height/2
    window.blit(Rect(0, 0, width, height), screen, Pos(x, y), 1.0, 0.7)
 
    #present the root console to the player and wait for a key-press
    screen.flush()
    key = console.wait_for_keypress(True)
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        console.toggle_fullscreen()
 
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def msgbox(text, width=50):
    menu(text, [], width) 
