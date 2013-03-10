from geometry import *
import libtcodpy as libtcod
import tiles

def rand(min,max): 
    return libtcod.random_get_int(0, min, max)

bsp_depth = 8
bsp_min_room_size = 9
# a room fills a random part of the node or the maximum available space ?
bsp_random_room = True
# if true, there is always a wall on north & west side of a room
bsp_room_walls = True
bsp_tunnels = 4

# Class that uses binary-space partitioning to generate rooms.
# Adapted from samples_py.py
class BSPGenerator:

    def __init__(self, map):
        self.map = map

    # Fills a line to a room
    def line2room(self, p1, p2=None, delta=None, stop_blocked = True):
        apply_function = lambda map, xy: map[xy].clear()
        stop_condition = lambda map, xy: not map[xy].blocked if stop_blocked else None
        self.map.apply_to_line(apply_function, p1, p2, delta, stop_condition)
#        if not delta:
#            delta = Pos( cmp(p2.x, p1.x), cmp(p2.y, p1.y ) )
#
#        points = []
#
#        p = Pos(p1.x, p1.y)
#        while p2 == None or p - delta != p2:
#            points.append(p)
#            p += delta
#            if not self.map.valid_xy(p): return False
#            if stop_blocked and not self.map[p].blocked: break
#
#        for p in points: self.map[p].clear()

    # draw a vertical line
    def vline(self, x, y1, y2):
        self.line2room( Pos(x, y1), Pos(x, y2) )
    
    # draw a vertical line up until we reach an empty space
    def vline_up(self, x, y):
        self.line2room( Pos(x, y), delta= Pos(0, -1))
    
    # draw a vertical line down until we reach an empty space
    def vline_down(self, x, y):
        self.line2room( Pos(x, y), delta= Pos(0, 1))
    
    # draw a horizontal line
    def hline(self, x1, y, x2):
        self.line2room( Pos(x1, y), Pos(x2, y) )
    
    # draw a horizontal line left until we reach an empty space
    def hline_left(self, x, y):
        self.line2room( Pos(x, y), delta= Pos(-1, 0))

    # draw a horizontal line right until we reach an empty space
    def hline_right(self, x, y):
        self.line2room( Pos(x, y), delta= Pos(+1, 0))

    def create_corridor(self, node, left, right):
        # create a corridor between the two lower nodes
        if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
            # vertical corridor
            if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                # no overlapping zone. we need a Z shaped corridor
                x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
                x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
                y = libtcod.random_get_int(None, left.y + left.h, right.y)
                self.vline_up(x1, y - 1)
                self.hline(x1, y, x2)
                self.vline_down(x2, y + 1)
            else:
                # straight vertical corridor
                minx = max(left.x, right.x)
                maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                x = libtcod.random_get_int(None, minx, maxx)
                self.vline_down(x, right.y)
                self.vline_up(x, right.y - 1)
        else:
            # horizontal corridor
            if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                # no overlapping zone. we need a Z shaped corridor
                y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                x = libtcod.random_get_int(None, left.x + left.w, right.x)
                self.hline_left(x - 1, y1)
                self.vline(x, y1, y2)
                self.hline_right(x + 1, y2)
            else:
                # straight horizontal corridor
                miny = max(left.y, right.y)
                maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                y = libtcod.random_get_int(None, miny, maxy)
                self.hline_left(right.x - 1, y)
                self.hline_right(right.x, y)

    # the class building the dungeon from the bsp nodes
    def traverse_node(self, node, dat):
        if libtcod.bsp_is_leaf(node):
            # calculate the room size
            minx = node.x + 1
            maxx = node.x + node.w - 1
            miny = node.y + 1
            maxy = node.y + node.h - 1
            if not bsp_room_walls:
                if minx > 1:
                    minx -= 1
                if miny > 1:
                    miny -= 1
            if maxx == self.map.size.w - 2:
                maxx -= 1
            if maxy == self.map.size.h - 2:
                maxy -= 1
            if bsp_random_room:
                minx = libtcod.random_get_int(None, minx, maxx - bsp_min_room_size + 1)
                miny = libtcod.random_get_int(None, miny, maxy - bsp_min_room_size + 1)
                maxx = libtcod.random_get_int(None, minx + bsp_min_room_size - 1, maxx)
                maxy = libtcod.random_get_int(None, miny + bsp_min_room_size - 1, maxy)
            # resize the node to fit the room
            node.x = minx
            node.y = miny
            node.w = maxx - minx + 1
            node.h = maxy - miny + 1
            # dig the room
            for x in range(minx, maxx + 1):
                for y in range(miny, maxy + 1):
                    self.map[Pos(x, y)].clear()
        else:
            # resize the node to fit its sons
            for i in range(bsp_tunnels): 
                left = libtcod.bsp_left(node)
                right = libtcod.bsp_right(node)
                node.x = min(left.x, right.x)
                node.y = min(left.y, right.y)
                node.w = max(left.x + left.w, right.x + right.w) - node.x
                node.h = max(left.y + left.h, right.y + right.h) - node.y
                self.create_corridor(node, left, right)
        return True
    def fill(self):
        bsp = libtcod.bsp_new_with_size(1, 1, self.map.size.w - 2, self.map.size.h - 2)
        libtcod.bsp_split_recursive(bsp, 0, bsp_depth,
                                    bsp_min_room_size +1,
                                    bsp_min_room_size +1, 2, 2)

        libtcod.bsp_traverse_inverted_level_order(bsp, lambda node, dat: self.traverse_node(node,dat) )

        libtcod.bsp_delete(bsp)
