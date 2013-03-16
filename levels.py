import libtcodpy as libtcod

import abilities
import enemies
import resource
import items
import workerants

from geometry import *
from tiles import *
from utils import *
from colors import *

class LevelTemplate:
    def __init__(self, handler, size, depth=8, min_node_size=5, maxHRatio=2, maxVRatio=2):
        self.depth = depth
        self.handler = handler
        self.min_node_size = min_node_size
        self.maxHRatio = maxHRatio
        self.maxVRatio = maxVRatio
        self.size = size
    def generate(self, level):
        import bspgenerator
        bsp = bspgenerator.BSPGenerator(level.map, self.size)
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

def place_resource_of_type(level, rxy, xy_region, resource_func, item_type):
    for i in range(len(xy_region)):
        level.add( resource_func(xy_region[i], i) )
        edges = list( make_rect(rxy - Pos(1,1), Size(4,4)).edge_values() )
    item_xy = edges[ rand(0,len(edges)-1) ]
    level.add( items.ItemObject(item_xy, item_type) )

def place_resource(level, min_dist = None):
    while True:
            rxy = level.random_xy()
            if min_dist:
                res = filter(lambda obj: isinstance(obj, resource.Resource), level.objects )
                if res:
                    dist_to_resource = min( [ rxy.sqr_distance(r.xy) for r in res ] )
                    if dist_to_resource < min_dist:
                        continue

            xy_near = [ rxy + Pos(x,y) for y in range(-1,3) for x in range(-1,3) ]
            valid = not any ( not level.map.valid_xy(xy) or level.is_solid(xy) for xy in xy_near )
            if valid:
                xy_region = [ rxy + Pos(x,y) for y in range(2) for x in range(2) ]
                type = rand(0, 2)
                if type == 0: 
                    place_resource_of_type(level, rxy, xy_region, resource.watermelon, items.WATERMELON_CHUNK)
                elif type == 1:
                    place_resource_of_type(level, rxy, xy_region, resource.orange, items.ORANGE_CHUNK)
                elif type == 2:
                    place_resource_of_type(level, rxy, xy_region, resource.apple, items.APPLE_CHUNK)
                break

def place_ant_holes(level, amount, min_dist = 7, max_dist = 13):
    for i in range(amount):
        while True:
            xy = level.random_xy(lambda level, xy: not level.map[xy].blocked and not any(level.objects_at(xy)))
            res = filter(lambda obj: isinstance(obj, resource.Resource), level.objects )
            dist_to_resource = min( [ xy.distance(r.xy) for r in res ] )
            if dist_to_resource >= min_dist and dist_to_resource <= max_dist:
                level.add( workerants.WorkerAntHole(xy) )
                break

def place_diggables(level, amount):
    apply_nearby(level.map, amount,
                 lambda xy: not level.is_solid(xy),
                 lambda tile: tile.type == WALL or tile.type == DIGGABLE,
                 lambda tile: tile.make_diggable()
    )

def add_floor_variety(level, nodes, chance=0.25):
    for node in nodes:
        if libtcod.bsp_is_leaf(node):
            mutator = Tile.make_floor2 if rand(0,2) == 1 else Tile.make_floor3
            if rand(0,999)/1000.0 < chance:
                rect = Rect(node.x, node.y, node.w, node.h)
                for xy in rect.xy_values():
                    if level.map[xy].type == FLOOR:
                        mutator(level.map[xy])

def wall2diggable(level, amnt):
    for i in range(amnt):
        xy = level.random_xy( lambda level,xy: level.map[xy].type == WALL )
        level.map[xy].make_diggable()

def place_enemies(level, *weights):
    for w in range(0, len(weights), 2):
        amount, type = weights[w], weights[w+1]
        for i in range(amount):
            xy = level.random_xy()
            level.add( type(xy) )
    level.enemy_spawner.set_weights(weights)

def win_template(hpgain, mpgain, rank):
    from globals import world
    from menus import msgbox

    stats = world.player.stats
    stats.max_hp += hpgain
    stats.max_mp += mpgain
    world.player.rank = rank
    world.messages.clear()
    world.messages.add([ GREEN, "You travel to a more dangerous land!"])
    world.messages.add([ BABY_BLUE, "You have mutated! You gain "+str(hpgain)+" HP and "+str(mpgain)+" MP!"])
    msgbox((BABY_BLUE, "You have harvested enough to feed this sector!\n", 
                  BABY_BLUE, "You have been promoted to ", YELLOW, world.player.rank+".\n",
                  BABY_BLUE,"Your skills are required in a more dangerous sector."), 55)

level_templates = []

def level1(level, bsp, nodes):
    for node in nodes: bsp.fill_node(node)
    for i in range(1): place_resource(level)
    place_diggables(level, 200)
    add_floor_variety(level, nodes)
    place_ant_holes(level, 2, min_dist=9,max_dist=14)
    wall2diggable(level, 200)
    place_enemies(level, 20, enemies.ant)
    level.enemy_spawner.enemy_maximum = 0 # turn off spawner
    level.points_needed = 40

    def win():
        from globals import world
        win_template(10, 5, "Lieutenant")
        world.player.stats.abilities.add( abilities.spit() )
        world.messages.add([ GREEN, "You gain the power of corrosive spit!"])

    level.win_function = win

level_templates.append( LevelTemplate(level1, size = Size(30,30), min_node_size=8) )

def level2(level, bsp, nodes):
    for node in nodes: bsp.fill_node(node)
    for i in range(2): place_resource(level)
    place_diggables(level, 400)
    add_floor_variety(level, nodes)
    place_ant_holes(level, 4, min_dist=9,max_dist=14)
    wall2diggable(level, 200)
    place_enemies(level, 25, enemies.ant, 4, enemies.roach, 6, enemies.ladybug)
    level.points_needed = 80

    def win():
        from globals import world
        win_template(10, 5, "Captain")

    level.win_function = win
level_templates.append( LevelTemplate(level2, size = Size(50,35), min_node_size=8) )

def level3(level, bsp, nodes):
    for node in nodes: bsp.fill_node(node)
    for i in range(2): place_resource(level, min_dist=35)
    place_diggables(level, 400)
    add_floor_variety(level, nodes)
    place_ant_holes(level, 7, min_dist=9,max_dist=14)
    wall2diggable(level, 200)
    place_enemies(level,  45, enemies.ant, 6, enemies.roach, 6, enemies.ladybug)
    level.enemy_spawner.enemy_maximum = 100
    level.points_needed = 80

    def win():
        from globals import world
        win_template(10, 5, "Major")
        world.messages.add([ GREEN, "You gain the power to spray acid!"])

    level.win_function = win

level_templates.append( LevelTemplate(level3, size = Size(80,33), min_node_size=8) )

def level4(level, bsp, nodes):
    for node in nodes: bsp.fill_node(node)
    for i in range(2): place_resource(level, min_dist=35)
    place_diggables(level, 400)
    add_floor_variety(level, nodes)
    place_ant_holes(level, 4, min_dist=9,max_dist=14)
    wall2diggable(level, 200)
    place_enemies(level, 85, enemies.ant, 6, enemies.roach, 6, enemies.ladybug, 1, enemies.beetle)
    level.enemy_spawner.enemy_maximum = 100
    level.points_needed = 80

    def win():
        from globals import world
        win_template(10, 5, "Colonel")

    level.win_function = win

level_templates.append( LevelTemplate(level4, size = Size(80,33), min_node_size=8) )


def level5(level, bsp, nodes):
    for node in nodes: bsp.fill_node(node)
    for i in range(3): place_resource(level, min_dist=25)
    place_diggables(level, 1100)
    add_floor_variety(level, nodes)
    place_ant_holes(level, 9, min_dist=9,max_dist=14)
    wall2diggable(level, 200)
    place_enemies(level, 65, enemies.ant, 25, enemies.roach, 15, enemies.ladybug, 3, enemies.beetle)
    level.enemy_spawner.enemy_maximum = 100
    level.points_needed = 120

    def win():
        from globals import world
        win_template(10, 5, "Colonel")

    level.win_function = win
level_templates.append( LevelTemplate(level4, size = Size(80,33), min_node_size=6) )

def generate_level(world, num):
    from globals import LEVEL_SIZE
    from dungeon import DungeonMap, DungeonLevel
    from scents import ScentMaps

    if num >= len(level_templates):
        return None

    new_map = DungeonMap(world, LEVEL_SIZE)
    scent_map = ScentMaps(world, LEVEL_SIZE)
    level = DungeonLevel(world, new_map, scent_map, num)

    level_templates[num].generate(level)

    return level
