import libtcodpy as libtcod
from globals import panel
from geometry import *

def render_bar(xy, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    panel.set_default_background(back_color)
    panel.rect( make_rect( xy, Size(total_width, 1)), False, libtcod.BKGND_SCREEN)
 
    #now render the bar on top
    panel.set_default_background(bar_color)
    if bar_width > 0:
        panel.rect( make_rect(xy, Size(bar_width, 1)), False, libtcod.BKGND_SCREEN)
 
    #finally, some centered text with the values
    panel.set_default_foreground(libtcod.white)

    panel.print_ex(Pos(xy.x + total_width / 2, xy.y), 
                   libtcod.BKGND_NONE, libtcod.CENTER,
                   name + ': ' + str(value) + '/' + str(maximum))