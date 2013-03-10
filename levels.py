
#bsp_depth = 8
#bsp_min_room_size = 9
## a room fills a random part of the node or the maximum available space ?
#bsp_random_room = True
## if true, there is always a wall on north & west side of a room
#bsp_room_walls = True
#bsp_tunnels = 4

import libtcodpy as libtcod
from geometry import *
import dungeonfeatures
from tiles import *

class LevelTemplate:
    def __init__(self, handler, depth=8, min_node_size=5, maxHRatio=2, maxVRatio=2):
        self.depth = depth
        self.handler = handler
        self.min_node_size = min_node_size
        self.maxHRatio = maxHRatio
        self.maxVRatio = maxVRatio
    def generate(self, level):
        import bspgenerator
        bsp = bspgenerator.BSPGenerator(level.map)
        nodes = bsp.split(self.depth, self.min_node_size, self.maxHRatio, self.maxVRatio)
        self.handler(level, bsp, nodes)

def rand(min,max): 
    return libtcod.random_get_int(0, min, max)
def rand_pos(max_x, max_y):
    return Pos( rand(0, max_x), rand(0, max_y) )

# Allows iteration of nearby squares
def nearby(map, xy):
    for y in range(xy.y-1, xy.y+2):
        for x in range(xy.x-1, xy.x+2):
            nearby_xy = Pos(x,y)
            if map.valid_xy(nearby_xy) and nearby_xy != xy:
                yield nearby_xy

def apply_nearby(map, points, tile_cond, near_cond, mutator):
    for i in range(points):
        while True:
            xy = rand_pos(map.size.w - 1, map.size.h - 1)
            if tile_cond(map[xy]) and any( near_cond(map[nxy]) for nxy in nearby(map, xy) ):
                mutator(map[xy])
                break

def _free_square(level, xy):
    return not level.map[xy].blocked and not any(level.objects_at(xy))

def level1(level, bsp, nodes):
    for node in nodes: 
        bsp.fill_node(node)

    apply_nearby(level.map, 1000,
                 lambda tile: not tile.blocked, 
                 lambda tile: tile.type is WALL or tile.type is DIGGABLE,
                 lambda tile: tile.make_diggable()
    )

    for node in nodes:
        if libtcod.bsp_is_leaf(node):
            if rand(0,5) == 1:
                rect = Rect(node.x, node.y, node.w, node.h)
                for xy in rect.xy_values():
                    level.map[xy].make_floor2()


#    # Stairs down
#    for i in range(2):
#        xy = level.random_xy(_free_square)
#        level.add( dungeonfeatures.Stairs(xy, stairs_down=True) )

LEVEL_1 = LevelTemplate(level1)

level_templates = [ LEVEL_1 ]

def generate_level(world, num):
    from globals import LEVEL_SIZE
    from dungeon import DungeonMap, DungeonLevel
    new_map = DungeonMap(world, LEVEL_SIZE)
    level = DungeonLevel(world, new_map, num)

    level_templates[num].generate(level)

    return level