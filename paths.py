import libtcodpy as libtcod
from geometry import Pos
import colors
from tiles import *

# Pathfinding class that copies from the game world

class PathFinder:
    def __init__(self, size, consider_unexplored_blocked = False, allow_digging = False):
        self.map = libtcod.map_new(size.w, size.h)
        self.path = libtcod.path_new_using_map(self.map)
        self.consider_unexplored_blocked = consider_unexplored_blocked
        self.allow_digging = allow_digging
    
    def __del__(self):
        libtcod.map_delete(self.map)
        libtcod.path_delete(self.path)
        self.map, self.path = None, None

    def compute_path(self, from_xy, to_xy, dungeonmap):
        for xy in dungeonmap.rect().xy_values():
            tile = dungeonmap[xy]
            block_sight, blocked = tile.block_sight, tile.blocked
            if self.allow_digging:
                blocked = blocked and not tile.type == DIGGABLE
            if self.consider_unexplored_blocked:
                blocked = blocked or not tile.explored
            libtcod.map_set_properties(self.map, xy.x, xy.y, block_sight, not blocked)
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
def towards(start_xy, to_xy, allow_digging = False):
    from globals import world, con
    path = PathFinder( world.level.size, consider_unexplored_blocked = True, allow_digging = allow_digging )
    path.compute_path(start_xy, to_xy, world.level.map)
    if path.size() == 0: 
        return None
    return path.get_node(0)
