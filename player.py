import libtcodpy as libtcod
from actions import *
import globals
import colors
from geometry import * 
from utils import *
import paths

import dungeonfeatures
from combatobject import CombatStats, CombatObject
from resource import Resource
from tiles import *
import enemies
import colors

PLAYER = TileType( 
        # ASCII mode
         { "char" : '@', "color" : colors.YELLOW },
        # Tile mode
         { "char" : tile(3,0) }
)

class PlayerStats:
    def __init__(self, hp, attack):
        self.hp = hp
        self.max_hp = hp
        self.attack = attack

class Player(CombatObject):
    def __init__(self, xy): 
        CombatObject.__init__(self, xy, PLAYER, 
                 CombatStats(hp = 100, mp = 50, mp_regen = 0.25, attack = 10))
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        self.damage_for_step = 0
    def take_damage(self, damage):
        self.damage_for_step += damage
        CombatObject.take_damage(self, damage)

    def die(self):
        from globals import world
        world.restart()

    def _adjust_view(self):
        PADDING = globals.VIEW_PADDING

        map_size = globals.world.level.size

        vx, vy = self.view.x, self.view.y
        vw, vh = self.view.w, self.view.h

        x, y = self.xy.x, self.xy.y

        if vx + PADDING > x: vx = x - PADDING
        elif vx + vw - PADDING < x: vx = x - vw + PADDING

        if vy + PADDING > y: vy = y - PADDING
        elif vy + vh - PADDING < y: vy = y - vh + PADDING
 
        vx = max(0, min(map_size.w - vw, vx))
        vy = max(0, min(map_size.h - vh, vy))

        self.view = Rect(vx, vy, vw, vh)

    def step(self):
        assert self.action # We shouldn't step unless we have an action

        self.damage_for_step = 0
        level = globals.world.level

        self.action.perform(self)
        self.action = None

        self.stats.regen_for_step()

        if level.map[self.xy].type == DIGGABLE:
            level.map[self.xy].make_floor()

        for obj in level.objects_at(self.xy):
            if isinstance(obj, dungeonfeatures.Stairs):
                # Transfer from level, but do it next turn
                new_index = level.level_index + (+1 if obj.stairs_down else -1)
                new_level = globals.world[new_index]
                new_level.add_to_front(self)
                new_level.queue_relocation(self, new_level.random_xy() )
                level.queue_removal(self)

        self._adjust_view()

    def queue_move(self, dx, dy):
        pos = self.xy + Pos(dx, dy)
        map = globals.world.level.map
        allow_dig = not console.is_key_pressed(libtcod.KEY_SHIFT)
        if map.valid_xy(pos):
            for object in globals.world.level.objects_at(pos):
                if isinstance(object, enemies.Enemy):
                    self.action = AttackAction(object)
                    return True
            if (allow_dig and map[pos].type == DIGGABLE) or not map[pos].blocked:
                self.action = MoveAction(pos)
                return True
        return False

    def has_action(self, key, mouse):
        assert self.action == None # Did we handle the last action ? 

        if key.vk == libtcod.KEY_UP or key.c == ord('k'):
            return self.queue_move( 0, -1 )
        elif key.vk == libtcod.KEY_DOWN or key.c == ord('j'):
            return self.queue_move( 0, +1 )
        elif key.vk == libtcod.KEY_LEFT or key.c == ord('h'):
            return self.queue_move( -1, 0 )
        elif key.vk == libtcod.KEY_RIGHT or key.c == ord('l'):
            return self.queue_move( +1, 0 )
        elif key.c == ord('b'):
            return self.queue_move( -1, +1 )
        elif key.c == ord('n'):
            return self.queue_move( +1, +1 )
        elif key.c == ord('y'):
            return self.queue_move( -1, -1 )
        elif key.c == ord('u'):
            return self.queue_move( +1, -1 )
        elif key.vk == libtcod.KEY_SPACE or key.c == ord('.'):
            return self.queue_move( 0, 0 )
        elif key.c == ord('m'):
            for obj in globals.world.level.objects_at(self.xy):
                if type(obj) == Resource:
                    obj.waypoint = True
            return False
        if mouse.lbutton:
            allow_dig = not console.is_key_pressed(libtcod.KEY_SHIFT)
            map = globals.world.level.map
            mouse_xy = Pos(mouse.cx, mouse.cy)
            if map.valid_xy(mouse_xy) and map[mouse_xy].explored:
                new_xy = paths.towards( self.xy, mouse_xy, allow_dig )
                if new_xy:
                    self.action = MoveAction(new_xy)
                    return True
        return False
        
    def print_stats(self):
        import gui
        from globals import panel
        gui.render_bar( Pos(3,3), 20, "HP", int(self.stats.hp), self.stats.max_hp, colors.RED, colors.DARKER_GRAY )
        gui.render_bar( Pos(3,4), 20, "MP", int(self.stats.mp), self.stats.max_mp, colors.BLUE, colors.DARKER_GRAY )
        print_colored(panel, Pos(3, 0), colors.BABY_BLUE, 'ANT COLONEL')
        if self.damage_for_step > 0:
            print_colored(panel, Pos(3, 6), colors.LIGHT_RED, 'YOU TOOK ' + str(int(self.damage_for_step)) + ' DAMAGE')
        print_colored(panel, Pos(3, 1), colors.GOLD, 'A', colors.WHITE, 'bilities')
        print_colored(panel, Pos(14, 1), colors.GOLD, 'C', colors.WHITE, 'ontrols')
        print_colored(panel, Pos(23, 1), colors.GOLD, 'I', colors.WHITE, 'nventory')
        print_colored(panel, Pos(40, 3), colors.GREEN, 'STATUS:')
        print_colored(panel, Pos(40, 4), colors.PALE_GREEN, 'Looking for a place to settle.')