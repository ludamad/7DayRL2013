from libtcodpy import *
from geometry import *

# Wraps most console_* functions from libtcod, uses Console object for ones that take 'con' as first parameter
# Combines all 'x, y' fields into 'xy' field that takes a geometry.Pos object
# Combines all 'x, y, w, h' fields into a 'rect' field that takes a geometry.Rect object

def init_root(size, title, fullscreen=False, renderer=RENDERER_SDL):
    console_init_root(size.w, size.h, title, fullscreen, renderer)

set_custom_font   = console_set_custom_font
flush             = console_flush
wait_for_keypress = console_wait_for_keypress
is_window_closed  = console_is_window_closed
is_key_pressed    = console_is_key_pressed
is_fullscreen     = console_is_fullscreen
set_fullscreen    = console_set_fullscreen

def toggle_fullscreen():
    set_fullscreen(not is_fullscreen())

# To get the screen console, just use Console()
# To create a new console, use Console(size)
class Console:
    def __init__(self, size = None):
        if size != None:
            self.con = console_new(size.w, size.h)
        else: # Hack to let us define the screen console
            self.con = 0
        self.size = size

    def __del__(self): # garbage collect
        if self.con != 0 and self.con != None:
            console_delete(self.con)
            self.con = None

    def clear(self):
        return console_clear(self.con)

    def put_char(self, xy, c, flag=BKGND_DEFAULT):
        console_put_char(self.con, xy.x, xy.y, c, flag)
    
    def put_char_ex(self, xy, c, fore, back):
        console_put_char_ex(self.con, xy.x, xy.y, c, fore, back)
    
    def set_default_foreground(self, col):
        console_set_default_foreground(self.con, col)

    def set_default_background(self, col):
        console_set_default_background(self.con, col)

    def set_char_background(self, xy, col, flag=BKGND_SET):
        console_set_char_background(self.con, xy.x, xy.y, col, flag)
    
    def set_char_foreground(self, xy, col):
        console_set_char_foreground(self.con, xy.x, xy.y, col)
    
    def set_char(self, xy, c):
        console_set_char(self.con, xy.x, xy.y, c)
    
    def set_background_flag(self, flag):
        console_set_background_flag(self.con)
    
    def get_background_flag(self):
        return console_get_background_flag(self.con)
    
    def set_alignment(self, alignment):
        console_set_alignment(self.con, alignment)
    
    def get_alignment(self):
        return console_get_alignment(self.con)
    
    def print_text(self, xy, fmt):
        console_print(self.con, xy.x, xy.y, fmt)
    
    def print_ex(self, xy, flag, alignment, fmt):
        console_print_ex(self.con, xy.x, xy.y, flag, alignment, fmt)
    
    def print_rect(self, rect, fmt):
        console_print_rect(self.con, rect.x, rect.y, rect.w, rect.h, fmt)
    
    def print_rect_ex(self, rect, flag, alignment, fmt):
        console_print_rect_ex(self.con, rect.x, rect.y, rect.w, rect.h, flag, alignment, fmt)
    
    def get_height_rect(self, rect, fmt):
        return console_get_height_rect(self.con, rect.x, rect.y, rect.w, rect.h, fmt)
    
    def rect(self, rect, clr, flag=BKGND_DEFAULT):
        console_rect(self.con, rect.x, rect.y, rect.w, rect.h, clr, flag)
    
    def hline(self, xy, l, flag=BKGND_DEFAULT):
        console_hline(self.con, xy.x, xy.y, l, flag)
    
    def vline(self, xy, l, flag=BKGND_DEFAULT):
        console_vline(self.con, xy.x, xy.y, l, flag)
    
    def print_frame(self, rect, clear=True, flag=BKGND_DEFAULT, fmt=0):
        console_print_frame(self, rect.x, rect.y, rect.w, rect.h, flag, fmt)
    
    def set_color_control(self, fore, back) :
        console_set_color_control(self.con, fore, back)
    
    def get_default_background(self):
        return console_get_default_background(self.con)
    
    def get_default_foreground(self):
        return console_get_default_foreground(self.con)

    def get_char_background(self, xy):
        return console_get_char_background(self.con, xy.x, xy.y)
    
    def get_char_foreground(self, xy):
        return console_get_char_foreground(self.con, xy.x, xy.y)
    
    def get_char(self, xy):
        return console_get_char(self.con, xy.x, xy.y)

# fast color filling
    def fill_background(self, r,g,b) :
        console_fill_foreground(self.con, r, g, b)
    
    def fill_char(self, arr) :
        console_fill_char(self.con, arr)
            
    def load_asc(self, filename) :
        console_load_asc(self.con, filename)
    def save_asc(self, filename) :
        console_save_asc(self.con, filename)
    def load_apf(self, filename) :
        console_load_apf(self.con, filename)
    def save_apf(self, filename) :
        console_load_apf(self.con, filename)

    def blit(self, rect, dst, xy = Pos(0,0), ffade=1.0, bfade=1.0):
        console_blit(self.con, rect.x, rect.y, rect.w, rect.h, dst.con, xy.x, xy.y, ffade, bfade)

    def flush(self):
        if self.con == 0:
            console_flush()
