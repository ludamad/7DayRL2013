import libtcodpy as libtcod
import console
from geometry import *
from globals import *
import colors

libtcod.sys_set_fps(20)

console.set_custom_font('tiles18x18_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 16, 25 )
console.init_root(SCREEN_SIZE + Size(0, panel.size.h), 'FooQuest', False, libtcod.RENDERER_SDL)

#libtcod.console_set_keyboard_repeat(30, 30)

while not console.is_window_closed():
    world.step()
    game_draw()