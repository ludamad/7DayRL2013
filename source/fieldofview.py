import libtcodpy as libtcod
from geometry import *

# Computes field of view
# Internally stores a small area that bounds the field-of-view
# Everything outside this area is returned as non-visible

class FieldOfView:
    def __init__(self, maxradius):
        self.start_xy = Pos(0,0)
        self.radius = 0
        self.size = Size( (maxradius + 1)*2, (maxradius + 1)*2 )
        self.map = libtcod.map_new(self.size.w, self.size.h)

    def __del__(self): # garbage collect
        libtcod.map_delete(self.map)
        self.map = None

    # private
    def _copy_from_dungeonmap(self, dungeonmap):
        area = make_rect(self.start_xy, self.size)
        for xy in area.xy_values():
            block_sight, blocked = True, True
            
            # Copy visibility information from dungeon, if we are not out of room bounds
            if dungeonmap.valid_xy(xy):
                tile = dungeonmap[xy]
                block_sight, blocked = tile.block_sight, tile.blocked

            # Store in our own buffer
            fov_xy = xy - self.start_xy
            libtcod.map_set_properties(self.map, fov_xy.x, fov_xy.y, not block_sight, blocked)

    def compute_fov(self, dungeonmap, xy, radius ):
        self.start_xy = xy - Pos(radius, radius)
        self.radius = radius
        # Copy visiblity information
        self._copy_from_dungeonmap(dungeonmap)

        fov_xy = xy - self.start_xy
        libtcod.map_compute_fov(self.map, fov_xy.x, fov_xy.y, radius, True, libtcod.FOV_PERMISSIVE_4)

    def is_visible(self, xy):
        area = make_rect(self.start_xy, self.size)
        if not area.within(xy): return False

        # check within radius
        source_xy = self.start_xy + Pos(self.radius, self.radius)
        if xy.distance(source_xy) >= self.radius: return False

        fov_xy = xy - self.start_xy
        return libtcod.map_is_in_fov(self.map, fov_xy.x, fov_xy.y)