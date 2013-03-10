import libtcodpy as libtcod
from geometry import Pos

def rand(min,max): 
    return libtcod.random_get_int(0, min, max)

def nearby(map, xy):
    for y in range(xy.y-1, xy.y+2):
        for x in range(xy.x-1, xy.x+2):
            nearby_xy = Pos(x,y)
            if map.valid_xy(nearby_xy) and nearby_xy != xy:
                yield nearby_xy

def random_nearby(level, xy, condition):
    candidates = filter(condition, nearby(level.map, xy))
    if candidates == []:
        return None
    return candidates[ rand(0, len(candidates)-1) ]