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

def print_colored(con, xy, *parts):
    for i in range(0, len(parts), 2):
        color, text = parts[i], parts[i+1]
        con.set_default_foreground(color)
        con.print_text( xy, text)
        xy += Pos( len(text), 0)