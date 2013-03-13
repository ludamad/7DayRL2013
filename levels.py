import libtcodpy as libtcod

import enemies
import resource
import items

from geometry import *
from tiles import *
from utils import *

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

def place_resource_of_type(level, rxy, xy_region, resource_func, item_type, item_chance):                
    for i in range(len(xy_region)):
        level.add( resource_func(xy_region[i], i) )
        edges = list( make_rect(rxy - Pos(1,1), Size(4,4)).edge_values() )
    item_xy = edges[ rand(0,len(edges)) ]
    level.add( items.ItemObject(item_xy, item_type) )

def place_resource(level, item_chance = 0.05):
    while True:
            rxy = level.random_xy()
            xy_near = [ rxy + Pos(x,y) for y in range(-1,3) for x in range(-1,3) ]
            valid = not any ( not level.map.valid_xy(xy) or level.is_solid(xy) for xy in xy_near )
            if valid:
                xy_region = [ rxy + Pos(x,y) for y in range(2) for x in range(2) ]
                type = rand(0, 3)
                if type == 0: 
                    place_resource_of_type(level, rxy, xy_region, resource.watermelon, items.WATERMELON_CHUNK, item_chance)
                elif type == 1:
                    place_resource_of_type(level, rxy, xy_region, resource.orange, items.ORANGE_CHUNK, item_chance)
                elif type == 2:
                    place_resource_of_type(level, rxy, xy_region, resource.apple, items.APPLE_CHUNK, item_chance)
                break
                 
def level1(level, bsp, nodes):
    for node in nodes: 
        bsp.fill_node(node)

    for i in range(4):
        place_resource(level)

    apply_nearby(level.map, 1100,
                 lambda xy: not level.is_solid(xy),
                 lambda tile: tile.type == WALL or tile.type == DIGGABLE,
                 lambda tile: tile.make_diggable()
    )

    for node in nodes:
        if libtcod.bsp_is_leaf(node):
            mutator = Tile.make_floor2 if rand(0,2) == 1 else Tile.make_floor3
            if rand(0,3) == 1:
                rect = Rect(node.x, node.y, node.w, node.h)
                for xy in rect.xy_values():
                    if level.map[xy].type == FLOOR:
                        mutator(level.map[xy])
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