import libtcodpy as libtcod
import console
from geometry import *
from globals import *
import colors

libtcod.sys_set_fps(20)

console.set_custom_font('tiles12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 16, 21 )
console.init_root(SCREEN_SIZE + Size(0, 7), 'FooQuest', False, libtcod.RENDERER_SDL)

screen = console.Console()
screen.set_default_foreground(colors.WHITE)

libtcod.console_set_keyboard_repeat(10, 25)

while not console.is_window_closed():
    world.step()

    # Draw the level to the buffer
    panel.set_default_background(colors.BLACK)
    panel.clear()
    world.draw()
    world.player.print_stats()

    # Blit it to the screen
    con.blit( make_rect(Pos(0,0), SCREEN_SIZE), screen )
    panel.blit( make_rect( Pos(0,0), panel.size), screen, Pos(0, 50))
    screen.flush()


