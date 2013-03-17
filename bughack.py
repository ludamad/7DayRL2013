import source.libtcodpy as libtcod
import source.console
from source.geometry import *
from source.globals import *
import source.colors

libtcod.sys_set_fps(20)

console.set_custom_font('tiles18x18_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 16, 25 )
console.init_root(SCREEN_SIZE + Size(0, panel.size.h), 'Bughack', False, libtcod.RENDERER_SDL)

#libtcod.console_set_keyboard_repeat(30, 30)

splash_screen(INTRO_IMAGE)
while not console.is_window_closed():
    world.step()
    game_draw()
