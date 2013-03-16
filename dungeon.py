from geometry import *
from generation import generate_map, generate_connected_map
from utils import *

import globals
import colors
import player
import fieldofview
import paths
import console
import tiles

from menus import menu, msgbox, Messages

WAS_SHOW_ALL = False
# Represents dungeon tiles
# Does not store game objects, DungeonLevel does that
class DungeonMap:
    def __init__(self, world, size):
        self.world = world
        self.size = size
        self.map = [ [ tiles.Tile(True) for x in range(size.w) ]
                        for y in range(size.h) ]

    def remember_tile(self, xy):
        tile = self[xy]
        tile.remembered_type = tile.type
        tile.remembered_variant = tile.variant

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
                tile = self[xy]
                if not SHOW_ALL:
                    if visible:
                        self.remember_tile(xy)
                    tile.explored = True
                tt, tv = tile.remembered_type, tile.remembered_variant
                if SHOW_ALL:
                    tt, tv = tile.type, tile.variant
                tiles.draw_tile(tt, tv, xy, True)

        WAS_SHOW_ALL = SHOW_ALL

# Holds a DungeonMap (ie, the tiles) and the game objects
class DungeonLevel:
    def __init__(self, world, map, scent_map, index):
        from enemyspawner import EnemySpawner
        from paths import PathFinder
        self.world = world
        self.map = map
        self.scents = scent_map
        self.objects = []
        self.path_finder = PathFinder(self.map.size)
        self.queued_removals = []
        self.queued_relocations = []
        self.good_things = []
        self.bad_things = []
        self.tile_memory =  [ [ None for x in range(map.size.w) ] for y in range(map.size.h) ]
        self.level_index = index
        self.enemy_spawner = EnemySpawner() # Default spawner
        self.points_needed = 80
        self.win_function = None

    @property
    def size(self): return self.map.size
    def objects_at(self, xy):
        return filter(lambda obj: obj.xy == xy, self.objects)

    def add(self, object):
        self.objects.append(object)
    def add_to_front(self, object):
        # Hack to always have player be first
        idx = 0 if self.world.player not in self.objects else self.objects.index(self.world.player)+1
        self.objects.insert(idx, object)
    # For corpses... yeah, hack, I know
    def add_to_front_of_combatobjects(self, object):
        from combatobject import CombatObject
        for i in reversed( range( len(self.objects) ) ):
            if isinstance( self.objects[i], CombatObject):
                self.objects.insert(i+1, object)
                return
        self.add(object)
    # For spawned combatobjects... yeah, hack, I know
    def add_to_back_of_corpses(self, object):
        from enemies import Corpse
        for i in range( len(self.objects)):
            if isinstance( self.objects[i], Corpse):
                self.objects.insert(i, object)
                return
        self.add(object)
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

    def objects_of_type(self, object_type):
        return filter(lambda obj: isinstance(obj, object_type), self.objects)

    def is_alive(self, object):
        return (object in self.objects) and (object not in self.queued_removals)
    def objects_of_team(self, team):
        from combatobject import CombatObject
        return filter(lambda obj: isinstance(obj, CombatObject) and obj.team == team, self.objects)

    def objects_of_type_at(self, xy, object_type):
        return filter(lambda obj: obj.xy == xy and isinstance(obj, object_type), self.objects)

    def draw(self, fulldraw=False):
        self.map.draw(fulldraw)
        for obj in self.objects: obj.draw()
        # hack to always draw player:
        self.world.player.draw()
    def step(self, key, mouse):
        from enemies import Enemy
        self.handle_relocations()

        if self.world.player.has_action(key, mouse):
            assert self.world.player.action
            self.scents.step()
            for obj in list(self.objects): 
                obj.step()
                if not self.is_alive(self.world.player):
                    break
            for obj in self.queued_removals: self.remove(obj)
            self.queued_removals = []
            self.enemy_spawner.step()

    def solid_object_at(self, xy, whitelist = None):
        return any( obj.solid and (not whitelist or not whitelist(obj) ) for obj in self.objects_at(xy))
    def is_solid(self, xy):
        return self.map[xy].blocked or self.solid_object_at(xy)

    def random_xy(self, func = None):
        if func == None:
            func = lambda level, xy: not level.map[xy].blocked and not self.solid_object_at(xy)
        rect = self.map.rect()
        while True:
            xy = Pos( rand(0, self.map.size.w-1), rand(0, self.map.size.h-1) )
            if func(self, xy):
                return xy

# Stores the game world.
class World:
    def __init__(self):
        from globals import SCREEN_SIZE

        self.levels = []

        self.fov = None
    
        # Initialize first level
        self.level = self[0]
        self.messages = Messages(7)
        self.player = player.Player(self.level.random_xy())
        self.level.add_to_front(self.player)

    @property
    def view(self):
        return self.player.view

    def restart(self):
        from globals import con
        con.clear()
        self.__init__()
        self.step()

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
        key = libtcod.Key()
        mouse = libtcod.Mouse()

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        key.c = ord( chr(key.c).lower() )

        if not self.fov:
            self.fov = fieldofview.FieldOfView(8)
            self.fov.compute_fov(self.level.map, self.player.xy, 8)

        if key.vk == libtcod.KEY_ESCAPE or libtcod.console_is_window_closed():
            if key.shift:
                exit()
            else:
                self.messages.add([colors.GREEN, "Press Shift+Escape to exit."])
        elif key.vk == libtcod.KEY_CONTROL:
            globals.ASCII_MODE = not globals.ASCII_MODE
            self.draw(True)
#        elif key.vk == libtcod.KEY_ENTER:
#            self.restart()
        elif key.c == ord('f'):
            console.toggle_fullscreen()
        else:
            self.level.step(key, mouse)
            if self.player not in self.level.objects:
                self.level.win_function()
                self.player.stats.hp = self.player.stats.max_hp
                self.player.stats.mp = self.player.stats.max_mp
                self.level = None
                # Where'd the player go ?
                for level in self.levels:
                    if self.player in level.objects:
                        self.level = level
                        break
                if not self.level:
                    globals.splash_screen(globals.VICTORY_IMAGE)
                    exit()
                self.level.handle_relocations()
                globals.screen.clear()
                self.fov.compute_fov(self.level.map, self.player.xy, 8)
                self.draw(fulldraw=True)

    def clear(self):
        self.levels = []
