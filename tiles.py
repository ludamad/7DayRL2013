from colors import *
import console
from libtcodpy import Color, KEY_SHIFT, KEY_CONTROL, random_get_int, KEY_DELETE, KEY_TAB

# This is messy! But theres a lot of details to handling both ASCII & tiles (with multiple variants) smoothly.
# It should just work, focus on the data below.
#
# A fallback color is one used when drawing over a floor tile - we cannot draw the floor tile on the bottom.

# Ensures its a valid (visible_color, not_visible_color) pair
def ensure_tuple(colors, default=None): 
    if colors is None: return default
    if type(colors) == tuple: return colors
    return (colors, colors * 0.5)
def ensure_list(value):
    return value if type(value) == list else [value]

# Picks from a (visible_color, not_visible_color) pair
def pick(colors, visible):
    return colors[0] if visible else colors[1]

class TileVariant:
    def __init__(self, char = ' ', color = WHITE, fallback = None, bg_color=None):
        self.char = char

        self.colors = ensure_tuple(color, (WHITE, WHITE*0.5))
        self.bg_colors = ensure_tuple(bg_color)
        self.fallback_colors = ensure_tuple(fallback, self.bg_colors)

    def draw(self, con, xy, visible, bg_fallback):
        if self.char == ' ': # Solid tile
            con.put_char_ex(xy, self.char, WHITE, pick(self.colors, visible))
        else:
            bg_fallback = bg_fallback or (BLACK, BLACK)
            bg_color = pick( self.bg_colors if self.bg_colors else bg_fallback, visible)
            con.put_char_ex(xy, self.char, pick(self.colors, visible), bg_color)

class TileType:
    def __init__(self, ascii_variants, tile_variants):
        self.ascii_variants = [TileVariant(**i) for i in ensure_list(ascii_variants) ]
        self.tile_variants = [TileVariant(**i) for i in ensure_list(tile_variants) ]

    def num_variants(self):
        return max( len(self.ascii_variants), len(self.tile_variants) )

    def variant(self, num): 
        from globals import ASCII_MODE
        variants = self.ascii_variants if ASCII_MODE else self.tile_variants
        return variants[ num % len(variants) ]

    def fallback_colors(self, num): 
        return self.variant(num).fallback_colors

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        # All tiles start unexplored
        self.explored = False
 
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.type = WALL # Defined below
        self.variant = random_get_int(0, 0, self.type.num_variants())

    def fallback_colors(self):
        return self.type.variant(self.variant).fallback_colors

    def make_floor(self):
        self.block_sight = False
        self.blocked = False
        self.type = FLOOR # Defined below
        self.variant = random_get_int(0, 0, self.type.num_variants())

    def make_floor2(self):
        self.block_sight = False
        self.blocked = False
        self.type = FLOOR2 # Defined below
        self.variant = random_get_int(0, 0, self.type.num_variants())

    def make_diggable(self):
        self.block_sight = True
        self.blocked = True
        self.type = DIGGABLE # Defined below
        self.variant = random_get_int(0, 0, self.type.num_variants())

def draw_tile(tt, num, xy, bg = False):
    SHOW_ALL = console.is_key_pressed(KEY_TAB)

    from globals import world, con, on_screen

    map, fov = world.level.map, world.fov
    visible = fov.is_visible(xy)
    tt.variant(num).draw( con, on_screen(xy), visible, map[xy].fallback_colors() )


# DATA -- the good part
# Provide the arguments to TileVariant() here, for all the ascii & tile variations
# Fallback is only needed for floor tiles!

# Returns a tile from the font
def tile(col,row):
    return 256+row*16+col
def variant_list(chars, properties):
    variants = []
    for char in chars:
        variant = dict(properties)
        variant["char"] = char
        variants.append(variant)
    return variants

DIGGABLE = TileType(   # ASCII mode
         { "color" : PALE_RED, 
           "char" : 176, 
           "bg_color" : (DARK_GRAY, DARKER_GRAY)}
        ,          # Tile mode
        variant_list(
            [ tile(1,2)]*5  + [ tile(1,3) , tile(1,4) , tile(2,2) ], 
            { "fallback" : Color(116, 46, 30) }
        )
)

WALL = TileType(   # ASCII mode
         { "color" : (LIGHT_RED, DARK_RED) }
        ,          # Tile mode
        { "char" : tile(2,3) }
)

FLOOR = TileType(  # ASCII mode
         { "char" : '.', 
           "color" : (WHITE, LIGHT_GRAY), 
           "bg_color" : (DARK_GRAY, DARKER_GRAY) }
        ,          # Tile mode
        variant_list(
            [ tile(0,1) ] + [ tile(1,1) ]*8, 
            { "fallback" : Color(190, 101, 58) }
        )
)

FLOOR2 = TileType(  # ASCII mode
         { "char" : '.', 
           "color" : (WHITE, LIGHT_GRAY), 
           "bg_color" : Color(100, 50, 30) }
        ,          # Tile mode
        variant_list(
            [ tile(2,4) ],
            { "fallback" : Color(194, 148, 88) }
        )
)