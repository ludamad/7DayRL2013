from geometry import *
import libtcodpy as libtcod
import tiles

def rand(min,max): 
    return libtcod.random_get_int(0, min, max)

# Class that uses binary-space partitioning to generate rooms.
# Adapted from samples_py.py
class BSPGenerator:

    def __init__(self, map):
        self.map = map
        self.bsp = libtcod.bsp_new_with_size(1, 1, self.map.size.w - 2, self.map.size.h - 2)

    # Fills a line to a room
    def line2room(self, p1, p2=None, delta=None, stop_blocked = True):
        apply_function = lambda map, xy: map[xy].make_floor()
        stop_condition = lambda map, xy: not map[xy].blocked if stop_blocked else None
        self.map.apply_to_line(apply_function, p1, p2, delta, stop_condition)

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

    def fill_node(self, node, tunnels=4, room_has_walls=True, min_size=6, random_fill=True):
        if libtcod.bsp_is_leaf(node):
            # calculate the room size
            minx = node.x + 1
            maxx = node.x + node.w - 1
            miny = node.y + 1
            maxy = node.y + node.h - 1
            if not room_has_walls:
                if minx > 1:
                    minx -= 1
                if miny > 1:
                    miny -= 1
            if maxx == self.map.size.w - 2:
                maxx -= 1
            if maxy == self.map.size.h - 2:
                maxy -= 1
            if random_fill:
                minx = libtcod.random_get_int(None, minx, maxx - min_size + 1)
                miny = libtcod.random_get_int(None, miny, maxy - min_size + 1)
                maxx = libtcod.random_get_int(None, minx + min_size - 1, maxx)
                maxy = libtcod.random_get_int(None, miny + min_size - 1, maxy)
            # resize the node to fit the room
            node.x = minx
            node.y = miny
            node.w = maxx - minx + 1
            node.h = maxy - miny + 1
            # dig the room
            for x in range(minx, maxx + 1):
                for y in range(miny, maxy + 1):
                    self.map[Pos(x, y)].make_floor()
        else:
            # resize the node to fit its sons
            for i in range(tunnels): 
                left = libtcod.bsp_left(node)
                right = libtcod.bsp_right(node)
                node.x = min(left.x, right.x)
                node.y = min(left.y, right.y)
                node.w = max(left.x + left.w, right.x + right.w) - node.x
                node.h = max(left.y + left.h, right.y + right.h) - node.y
                self.create_corridor(node, left, right)
    def split(self, depth, min_size, maxHRatio = 2, maxVRatio = 2):
        libtcod.bsp_split_recursive(self.bsp, 0, depth,
                                    min_size +1,
                                    min_size +1, maxHRatio, maxVRatio)
        bsp_nodes = []
        def build_list(node, _):
            bsp_nodes.append(node)
            return True
        libtcod.bsp_traverse_inverted_level_order(self.bsp, build_list)

        return bsp_nodes

    def fill(self):
        nodes = self.split(8, 9)
        for node in nodes: self.fill_node(node)