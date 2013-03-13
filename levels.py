import libtcodpy as libtcod
from geometry import *
import dungeonfeatures
from tiles import *
import enemies
from utils import *
import resource
import items

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
            if tile_cond(xy) and any( near_cond(map[nxy]) for nxy in nearby(map, xy) ):
                mutator(map[xy])
                break

def _free_square(level, xy):
    return not level.map[xy].blocked and not any(level.objects_at(xy))

def place_resource(level, food_chance = 0.2):
    while True:
            rxy = level.random_xy()
            xy_near = [ rxy + Pos(x,y) for y in range(-1,3) for x in range(-1,3) ]
            valid = not any ( not level.map.valid_xy(xy) or level.is_solid(xy) for xy in xy_near )
            if valid:
                xy_region = [ rxy + Pos(x,y) for y in range(2) for x in range(2) ]
                for i in range(len(xy_region)):
                    level.add( resource.Resource(xy_region[i], i) )
                for xy in make_rect(rxy - Pos(1,1), Size(4,4)).edge_values():
                    if rand(0,100) / 100.0 <= food_chance:
                        level.add( items.ItemObject(xy, items.HEALING_FOOD) )
                break
                 
def level1(level, bsp, nodes):
    for node in nodes: 
        bsp.fill_node(node)

    for i in range(5):
        place_resource(level)

    apply_nearby(level.map, 1100,
                 lambda xy: not level.is_solid(xy),
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

    for i in range(200):
        xy = level.random_xy( lambda level,xy: level.map[xy].type == WALL )
        level.map[xy].make_diggable()


    for i in range(45):
        xy = level.random_xy()
        level.add( enemies.ant(xy) )

    for i in range(25):
        xy = level.random_xy()
        level.add( enemies.ladybug(xy) )

    for i in range(25):
        xy = level.random_xy()
        level.add( enemies.roach(xy) )


#    # Stairs down
#    for i in range(2):
#        xy = level.random_xy(_free_square)
#        level.add( dungeonfeatures.Stairs(xy, stairs_down=True) )

LEVEL_1 = LevelTemplate(level1)

level_templates = [ LEVEL_1 ]

def generate_level(world, num):
    from globals import LEVEL_SIZE
    from dungeon import DungeonMap, DungeonLevel
    from scents import ScentMaps
    new_map = DungeonMap(world, LEVEL_SIZE)
    scent_map = ScentMaps(world, LEVEL_SIZE)
    level = DungeonLevel(world, new_map, scent_map, num)


    level_templates[num].generate(level)

    return level