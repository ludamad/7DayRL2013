import libtcodpy as libtcod
from actions import *
import globals
import colors
from geometry import * 
import paths

import dungeonfeatures
from gameobject import GameObject
from tiles import TileType, tile
import colors

ANTPLAYER = TileType(
        # ASCII mode
         { "char" : '@', "color" : colors.WHITE },
        # Tile mode
         { "char" : tile(1,0) }
)

class AntPlayer(GameObject):
    def __init__(self, xy):
        GameObject.__init__(self, XY, ANTPLAYER)
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        
    def _adjust_view(self):
        PADDING = globals.VIEW_PADDING
        
        map_size = globals.world.level.size
        
        vx, vy = self.view.x, self.view.y
        vw, vh = self.view.w, self.view.h
        
        x, y = self.xy.x, self.xy.y
        
        if vx + PADDING > x: vx = x - PADDING
        elif vx + vw - PADDING < x: vx = x - vw + PADDING
        
        if vy + PADDING > y: vy = y - PADDING
        elif vy + vh - PADDING < y: vy = y - vh + PADDING
        
        vx = max(0, min(map_size.w - vw, vx))
        vy = max(0, min(map_size.h - vh, vy))
        
        self.view = Rect(vx, vy, vw, vh)
        
    def step(self):
            assert self.action # We shouldn't step unless we have an action
            level = globals.world.level
            
            self.action.perform(self)
            self.action = None
            
            level.map[self.xy].blocked = False
            level.map[self.xy].block_sight = False
            
            for obj in level.objects_at(self.xy):
                if isinstance(obj, dungeonfeatures.Stairs):
                    # Transfer from level, but do it next turn
                    new_index = level.level_index + (+1 if obj.stairs_down else -1)
                    new_level = globals.world[new_index]
                    new_level.add(self)
                    new_level.queue_relocation(self, new_level.random_xy() )
                    level.queue_removal(self)
                            
            self._adjust_view()
            
    def queue_move(self, dx, dy):
        pos = self.xy + Pos(dx, dy)
        map = globals.world.level.map
        if map.valid_xy(pos) and not map[pos].blocked:
            self.action = MoveAction(pos)
            return True
        return False