from geometry import *
from generation import generate_map, generate_connected_map, generate_features
from utils import *

import colors
import player
import fieldofview
import paths
import console
import tiles

from menus import menu, msgbox

WAS_SHOW_ALL = False
# Represents dungeon tiles
# Does not store game objects, DungeonLevel does that
class DungeonMap:
    def __init__(self, world, size):
        self.world = world
        self.size = size
        self.map = [ [ tiles.Tile(True) for x in range(size.w) ]
                        for y in range(size.h) ]

    # Convenience function for making a rectangle that spans the map
    def rect(self):
        return make_rect( Pos(0,0), self.size )

    # To allow for a = map[xy]
    def __getitem__(self, xy):
        return self.map[ xy.y ][ xy.x ]

    # To allow for map[xy] = a
    def __setitem__(self, xy, tile):
        self.map[ xy.y ][ xy.x ] = tile

    # Test whether coordinate is valid within the map
    def valid_xy(self, xy):
        return xy.x >= 0 and xy.x < self.size.w and xy.y >= 0 and xy.y < self.size.h

    def apply_to_line(self, func, p1, p2=None, delta=None, stop_condition=None, abort_condition=None):
        if not delta:  delta = Pos( cmp(p2.x, p1.x), cmp(p2.y, p1.y ) )

        points = []

        while p2 == None or p1 - delta != p2:
            points.append(p1)
            p1 += delta
            abort = abort_condition and abort_condition(self, p1)
            if abort or not self.valid_xy(p1): return False
            if stop_condition and stop_condition(self, p1): break

        for p in points: func(self, p)

    # Defines a function that operates on a rectangle
    def apply_to_rect(self, func, rect):
        for xy in rect.xy_values():
            func(self[xy])

    def draw(self, fulldraw=False):
        from globals import on_screen, con

        global WAS_SHOW_ALL
        visible_area = make_rect( Pos(0,0), self.size )

        player_xy = self.world.player.xy
        view = self.world.view
        fov = self.world.fov

        # For debug purposes, show the screen
        SHOW_ALL = console.is_key_pressed(libtcod.KEY_TAB)
        if WAS_SHOW_ALL: 
            fulldraw = True
        if fulldraw:
            con.clear()

        FAST_RENDER_CUTOFF = 11
        for xy in view.xy_values():
            # Optimization: Don't render outside needed region
            if xy.distance(player_xy) > FAST_RENDER_CUTOFF and not (SHOW_ALL or fulldraw ): 
                continue

            visible = fov.is_visible(xy) or SHOW_ALL

            if not visible and not self[xy].explored:
                con.set_char_background( on_screen(xy), colors.BLACK, libtcod.BKGND_SET )
            else:
                if not SHOW_ALL:
                    self[xy].explored = True

                tiles.draw_tile(self[xy].type, self[xy].variant, xy, True)

        WAS_SHOW_ALL = SHOW_ALL

# Holds a DungeonMap (ie, the tiles) and the game objects
class DungeonLevel:
    def __init__(self, world, map, index):
        self.world = world
        self.map = map
        self.objects = []
        self.queued_removals = []
        self.queued_relocations = []
        self.level_index = index
    @property
    def size(self): return self.map.size
    def objects_at(self, xy):
        for obj in self.objects:
            if obj.xy == xy:
                yield obj
    def add(self, object):
        self.objects.append(object)
    def add_to_front(self, object):
        # Hack to always have player be first
        idx = 0 if self.world.player not in self.objects else self.objects.index(self.world.player)+1
        self.objects.insert(idx, object)
    def remove(self, object):
        self.objects.remove(object)
    def queue_removal(self, object):
        self.queued_removals.append(object)
    # Used when we transfer rooms, to specify the new xy after the current step
    def queue_relocation(self, object, xy):
        self.queued_relocations.append( (object, xy) )
    def handle_relocations(self):
        for obj, xy in self.queued_relocations: obj.xy = xy
        self.queued_relocations = []

        self.world.fov.compute_fov(self.map, self.world.player.xy, 8)
        
    def draw(self, fulldraw=False):
        self.map.draw(fulldraw)
        for obj in self.objects: obj.draw()
    def step(self, key, mouse):
        self.handle_relocations()

        if self.world.player.has_action(key, mouse):
            assert self.world.player.action
            for obj in list(self.objects): obj.step()
            for obj in self.queued_removals: self.remove(obj)
            self.queued_removals = []

    def solid_object_at(self, xy):
        return any( obj.solid for obj in self.objects_at(xy))
    def is_solid(self, xy):
        return self.map[xy].blocked or self.solid_object_at(xy)

    def random_xy(self, func = ( lambda level, xy: not level.map[xy].blocked )):
        rect = self.map.rect()
        while True:
            xy = Pos( rand(0, self.map.size.w-1), rand(0, self.map.size.h-1) )
            if func and func(self, xy):
                return xy

# Stores the game world.
class World:
    def __init__(self):
        from globals import SCREEN_SIZE

        self.levels = []

        self.fov = fieldofview.FieldOfView(8)

        # Initialize first level
        self.level = self[0]
        self.player = player.Player(self.level.random_xy())
        self.level.add_to_front(self.player)

    @property
    def view(self):
        return self.player.view

    def restart(self):
        from globals import con
        con.clear()
        self.__init__()

    # Gets or generates a level
    def __getitem__(self, idx):
        from globals import LEVEL_SIZE

        while idx >= len(self.levels):
            import levels

            self.levels.append( levels.generate_level(self, idx) )

        return self.levels[idx]

    def draw(self, fulldraw = False):
        self.level.draw(fulldraw)

    def step(self):
        import globals
        key = libtcod.Key()
        mouse = libtcod.Mouse()

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if key.vk == libtcod.KEY_ESCAPE:
            exit()
        elif key.vk == libtcod.KEY_CONTROL:
            globals.ASCII_MODE = not globals.ASCII_MODE
            self.draw(True)
        elif key.vk == libtcod.KEY_ENTER:
            self.restart()
        elif key.c == ord('f'):
            console.toggle_fullscreen()
        else:
            self.level.step(key, mouse)
            if self.player not in self.level.objects:
                # Where'd the player go ?
                for level in self.levels:
                    if self.player in level.objects:
                        self.level = level
                        break
                self.level.handle_relocations()
                self.draw(True)

    def clear(self):
        self.levels = []