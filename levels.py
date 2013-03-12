import libtcodpy as libtcod
from geometry import *
import dungeonfeatures
from tiles import *
import enemies
from utils import *
import resource

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
                 lambda tile: tile.type == WALL or tile.type == DIGGABLE,
                 lambda tile: tile.make_diggable()
    )

    for node in nodes:
        if libtcod.bsp_is_leaf(node):
            if rand(0,5) == 1:
                rect = Rect(node.x, node.y, node.w, node.h)
                for xy in rect.xy_values():
                    if level.map[xy].type == FLOOR:
                        level.map[xy].make_floor2()

    for i in range(50):
        xy = level.random_xy()
        level.add( enemies.ladybug(xy) )

    for i in range(5):
        while True:
            rxy = level.random_xy()
            xy_near = [ rxy + Pos(x,y) for y in [0,1] for x in [0,1] ]
            valid = not any ( not level.map.valid_xy(xy) or level.is_solid(xy) for xy in xy_near )
            if valid:
                for i in range(len(xy_near)):
                    level.add( resource.Resource(xy_near[i], i) )
                break

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