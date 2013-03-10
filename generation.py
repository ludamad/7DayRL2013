from geometry import *
import libtcodpy as libtcod
from bspgenerator import BSPGenerator
from dungeonfeatures import Stairs

def rand(min,max): 
    return libtcod.random_get_int(0, min, max)
def rand_pos(max_x, max_y):
    return Pos( rand(0, max_x), rand(0, max_y) )

def clear_tile(tile):
    tile.blocked = False
    tile.block_sight = False

def tunnel(map, p1, p2):
    map.apply_to_line( lambda map, xy: map[xy].make_floor() , p1, p2 )

# Allows iteration of nearby squares
def nearby(map, xy):
    for y in range(xy.y-1, xy.y+2):
        for x in range(xy.x-1, xy.x+2):
            nearby_xy = Pos(x,y)
            if map.valid_xy(nearby_xy) and nearby_xy != xy:
                yield nearby_xy

def apply_donuts(map, points, f = clear_tile):
    for i in range(points):
        xy = rand_pos(map.size.w - 1, map.size.h - 1)
        for n in nearby(map, xy): 
            f(map[n])

def apply_erode(map, points, f = clear_tile):
    for i in range(points):
        xy = rand_pos(map.size.w - 1, map.size.h - 1)
        if any( not map[nxy].blocked for nxy in nearby(map, xy) ):
            f(map[xy])

def generate_room(map, size_range):
    #random width and height
    min, max = size_range
    size = Size( rand(min, max),  rand(min, max) )
    #random position without going out of the boundaries of the map
    xy = Pos( rand(0, map.size.w - size.w - 1), rand(0, map.size.h - size.h - 1 ))
    room = make_rect( xy, size )
    
    map.apply_to_rect( clear_tile, room )
    return room

def generate_rooms(map, size_range, num_range):
    min, max = num_range
    num_rooms = rand(min, max)
    rooms = []
    for i in range(num_rooms):
        generate_room(map, size_range)

def generate_map(map):
    generate_rooms(map, (2, 4), (6, 15))
    generate_rooms(map, (5, 12), (4, 6))

    apply_donuts(map, 50)
    apply_erode(map, 2500)

# Generate connection rooms in the given region
def generate_connected_map(map):
    BSPGenerator(map).fill()

def _free_square(level, xy):
    return not level.map[xy].blocked and not any(level.objects_at(xy))

def generate_features(level):
    # Stairs down
    for i in range(2):
        xy = level.random_xy(_free_square)
        level.add( Stairs(xy, stairs_down=True) )