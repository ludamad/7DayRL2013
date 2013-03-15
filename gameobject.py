import tiles
import console
import libtcodpy as libtcod

class GameObject:
    def __init__(self, xy, tile_type, solid=True, draw_once_seen = False):
        self.xy = xy
        self.seen = False
        self.waypoint = False
        self.solid = solid
        self.tile_type = tile_type
        self.draw_once_seen = draw_once_seen
        self.tile_variant = 0
    def apply_scent(self, scents):
        pass
    def step(self):
        pass
    def draw(self):
        from globals import on_screen, world

        visible = world.fov.is_visible(self.xy) or console.is_key_pressed(libtcod.KEY_TAB)
        if visible or (world.level.map[self.xy].explored and self.draw_once_seen):
            tiles.draw_tile( self.tile_type, self.tile_variant, self.xy)
