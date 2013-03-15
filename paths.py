import libtcodpy as libtcod
from geometry import Pos
import colors
from tiles import *

# Pathfinding class that copies from the game world


def _path_xy_function(level, to_xy, avoid_solid_objects = False, consider_unexplored_blocked = True, allow_digging = False):
    def pather(from_x, from_y, x, y, userdata=None):
        tile = level.map.map[y][x]
        block_sight, blocked = tile.block_sight, tile.blocked
        if allow_digging:
            blocked = blocked and not tile.type == DIGGABLE
        if avoid_solid_objects and (x != to_xy.x or y != to_xy.y):
            blocked = blocked or level.solid_object_at(Pos(x,y))
        if consider_unexplored_blocked:
            blocked = blocked or not tile.explored
        return blocked
    return pather

class PathFinder:
    def __init__(self, size, avoid_solid_objects = False, consider_unexplored_blocked = False, allow_digging = False):
        self.path = libtcod.path_new_using_function(size.w, size.h, self.path_func, 1)
        self.consider_unexplored_blocked = consider_unexplored_blocked
        self.allow_digging = allow_digging
        self.avoid_solid_objects = avoid_solid_objects
        self._path_func = None
    def path_func(self, from_x, from_y, x, y, userdata):
        return self._path_func(from_x, from_y, x, y, userdata)

    def __del__(self):
        libtcod.map_delete(self.map)
        libtcod.path_delete(self.path)
        self.map, self.path = None, None

    def compute_path(self, from_xy, to_xy, path_function):
#        for xy in level.map.rect().xy_values():
#            tile = level.map[xy]
#            block_sight, blocked = tile.block_sight, tile.blocked
#            if self.allow_digging:
#                blocked = blocked and not tile.type == DIGGABLE
#            if self.avoid_solid_objects and xy != to_xy:
#                blocked = blocked or level.solid_object_at(xy)
#            if self.consider_unexplored_blocked:
#                blocked = blocked or not tile.explored
#            libtcod.map_set_properties(self.map, xy.x, xy.y, block_sight, not blocked)
        libtcod.path_compute(self.path, from_xy.x, from_xy.y, to_xy.x, to_xy.y)

    def get_node(self, idx):
        return Pos( *libtcod.path_get(self.path, idx))

    def size(self):
        return libtcod.path_size(self.path)

    def nodes(self):
        rr = range(self.path.size())
        return [ Pos( *libtcod.path_get(self.path, i) ) for i in rr ]

    def draw(self):
        from globals import con, on_screen
        for xy in self.nodes():
            con.put_char_ex(on_screen(xy), ' ', colors.WHITE, colors.YELLOW)

# Returns None if not possible
def towards(start_xy, to_xy, avoid_solid_objects = False, consider_unexplored_blocked = True, allow_digging = False):
    from globals import world, con
    pather = world.level.path_finder
    pather._path_func = _path_xy_function( world.level, to_xy,
                       avoid_solid_objects = avoid_solid_objects, 
                       consider_unexplored_blocked = consider_unexplored_blocked, 
                       allow_digging = allow_digging )
    pather.compute_path(start_xy, to_xy, world.level)
    if pather.size() == 0: 
        return None
    return pather.get_node(0)
