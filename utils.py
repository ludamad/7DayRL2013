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
    new_xy = xy
    for i in range(0, len(parts), 2):
        color, text = parts[i], parts[i+1]
        con.set_default_foreground(color)
        con.print_text( new_xy, text)
        new_xy += Pos( len(text), 0)
        if text[len(text)-1] == '\n':
            new_xy = Pos(xy.x, new_xy.y+1)
    return new_xy

def step_towards(from_xy, to_xy):
    libtcod.line_init(from_xy.x, from_xy.y, to_xy.x, to_xy.y)
    return Pos( *libtcod.line_step() )
