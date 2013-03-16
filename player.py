import libtcodpy as libtcod

import globals
import colors
import paths
import menus
import enemies
import abilities

from actions import *
from geometry import * 
from utils import *
from tiles import *

from combatobject import CombatStats, CombatObject, TEAM_PLAYER
from resource import Resource

PLAYER = TileType( 
        # ASCII mode
         { "char" : '@', "color" : colors.YELLOW },
        # Tile mode
         { "char" : tile(3,0) }
)

INVENTORY_LOCATION_IN_PANEL = Pos(25, 4)

def _get_mouse_item_slot(player, mouse):
    from globals import SCREEN_SIZE
    mouse_xy = Pos(mouse.cx, mouse.cy)
    xy = mouse_xy - Pos(0, SCREEN_SIZE.h) - INVENTORY_LOCATION_IN_PANEL
    return player.stats.inventory.find_clicked_item(xy)


class Player(CombatObject):
    def __init__(self, xy):
        # Starting stats, you gain more each level
        stats = CombatStats(hp = 50, mp = 20, mp_regen = 0.5, attack = 10)
        CombatObject.__init__(self, xy, PLAYER, stats, team = TEAM_PLAYER)

        self.rank = "Private"
        self.action = None
        self.view = make_rect(Pos(0,0), globals.SCREEN_SIZE)
        self.points = 0
        self.defence = 0
        self.stats.abilities.add( abilities.call_ants() )
        self.stats.abilities.add( abilities.bad_smell() )

    def attack(self, target):
        from globals import world
        world.messages.add( [colors.BABY_BLUE, 'You bite the ' + target.name + " for " + str(int(self.stats.attack)) + ' damage!'] )
        target.take_damage(self, self.stats.attack)
    def take_damage(self, attacker, damage):
        from globals import world
        from enemies import Enemy
        from workerants import WorkerAnt
        damage = max(0, damage - self.defence)
        if damage == 0:
            world.messages.add( [colors.GREEN, 'You defend the ' +attacker.name+ "'s attack!"] )
            return

        CombatObject.take_damage(self, attacker, damage)
        if isinstance(attacker, Enemy):
            world.messages.add( [colors.LIGHT_RED, 'The ' + attacker.name + ' bites you for ' + str(int(damage)) + ' damage!'] )
        elif isinstance(attacker, WorkerAnt):
            world.messages.add( [colors.PURPLE, 'A worker has died, you take ' + str(damage) + ' damage!'] )

    def apply_scent(self, scents):
        scents.apply_scent(self.xy, 100, 8)

    def die(self):
        from globals import world, splash_screen, DEFEAT_IMAGE
        from workerants import WORKER_ANT_DEAD_TILE
        self.tile_type = WORKER_ANT_DEAD_TILE
        world.messages.add([colors.RED, "You have died!"])
        splash_screen()
        splash_screen(DEFEAT_IMAGE)
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

        CombatObject.step(self)

        level = globals.world.level

        self.action.perform(self)

        globals.world.fov.compute_fov(globals.world.level.map, self.xy, 8)
        self.action = None

        if level.map[self.xy].type == DIGGABLE:
            level.map[self.xy].make_floor()

        self._adjust_view()

    def goto_next_level(self):
        level = globals.world.level
        # Transfer from level, but do it next turn
        new_index = level.level_index + 1
        new_level = globals.world[new_index]
        if new_level:
            new_level.add_to_front(self)
            new_level.queue_relocation(self, new_level.random_xy() )
        level.queue_removal(self)
        self.points = 0

    def queue_move(self, dx, dy):
        from workerants import WorkerAnt

        pos = self.xy + Pos(dx, dy)
        map = globals.world.level.map
        allow_dig = not console.is_key_pressed(libtcod.KEY_SHIFT)
        if map.valid_xy(pos):
            for object in globals.world.level.objects_at(pos):
                if isinstance(object, enemies.Enemy):
                    self.action = AttackAction(object)
                    return True
            whitelist = lambda o: isinstance(o, Player) or isinstance(o, WorkerAnt)
            solid_obj = globals.world.level.solid_object_at(pos, whitelist=whitelist)
            tile_walkable = (allow_dig and map[pos].type == DIGGABLE) or not map[pos].blocked
            if not solid_obj and tile_walkable:
                self.action = MoveAction(pos)
                return True
        return False

    def add_harvest_points(self, points):
        from globals import world
        self.points += points
        if self.points >= world.level.points_needed:
            self.goto_next_level()

    def queue_use_item(self, item_slot):
        self.action = UseItemAction(item_slot)
        return True

    def queue_use_ability(self, ability, target):
        self.action = UseAbilityAction(ability, target)
        return True

    def queue_drop_item(self, item_slot):
        from globals import world
        from items import ItemObject
        if not any( isinstance(obj, ItemObject) for obj in world.level.objects_at(self.xy) ):
            self.action = DropItemAction(item_slot)
            return True
        return False

    def queue_click_move(self, mouse):
        allow_dig = mouse.rbutton
        map = globals.world.level.map
        mouse_xy = Pos(mouse.cx, mouse.cy)
        if map[mouse_xy].explored:
            new_xy = paths.towards( self.xy, mouse_xy, avoid_solid_objects = True, allow_digging = allow_dig )
            if new_xy:
                rel_xy = new_xy - self.xy
                self.queue_move(rel_xy.x, rel_xy.y)
                return True
        return False

    def handle_clicks(self, mouse):
        map = globals.world.level.map
        mouse_xy = Pos(mouse.cx, mouse.cy)
        if (mouse.lbutton or mouse.rbutton) and map.valid_xy(mouse_xy):
            return self.queue_click_move(mouse)
        elif mouse.lbutton_pressed or mouse.rbutton_pressed:
            item_slot = _get_mouse_item_slot(self, mouse)
            if item_slot:
                if mouse.lbutton_pressed:
                    return self.queue_use_item(item_slot)
                elif mouse.rbutton_pressed:
                    return self.queue_drop_item(item_slot)
        return False

    def handle_inventory(self):
        from globals import game_draw
        items = self.stats.inventory.items
        text = "Which item do you want to use or drop?" if items else "You don't have any items."
        options = []
        for item_slot in items:
            options.append([colors.MUTED_GREEN, item_slot.item_type.name+" ", colors.YELLOW, item_slot.item_type.summary])
        opt = menus.menu((colors.GOLD, text), options, 70, index_color=colors.YELLOW)
        if opt == None:
            return False
        game_draw()
        use_or_drop = menus.menu((colors.GOLD, "Use the " + items[opt].item_type.name + ", or drop it ?"), [(colors.LIGHT_GREEN,"Use"), (colors.LIGHT_RED,"Drop")], 50, index_color=colors.YELLOW)
        if use_or_drop == 0:
            return self.queue_use_item(items[opt])
        elif use_or_drop == 1:
            return self.queue_drop_item(items[opt])
        return False
    
    def handle_abilities(self):
        from globals import game_draw
        abilities = self.stats.abilities
        text = "Which mutant ability shall you inflict?"
        options = []
        for ability in abilities:
            can_do = ability.has_prereqs(self)
            if can_do:
                options.append([colors.BABY_BLUE, str(ability.mana_cost) + " MP ", 
                                colors.LIGHT_GREEN, ability.name+" ", 
                                colors.WHITE, ability.summary])
            else:
                options.append([colors.BABY_BLUE if self.stats.mp > ability.mana_cost else colors.GRAY, str(ability.mana_cost) + " MP ", 
                                colors.GRAY, ability.name+" ", 
                                colors.DARK_GRAY, ability.summary])
        opt = menus.menu((colors.GOLD, text), options, 65, index_color=colors.YELLOW)
        if opt != None:
            ability = abilities[opt]
            target = ability.target(self)
            if target:
                return self.queue_use_ability(ability, target) 
        return False

    def handle_controls(self):
        controls = [ colors.GREEN, "Arrow key ",
                    colors.WHITE, "movement accepted, but cannot do diagonals\n", colors.WHITE, '\n']
        controls += [colors.GREEN, "'.'", colors.WHITE, " or ", colors.GREEN, "5", colors.WHITE, ' to wait a turn\n', colors.WHITE, '\n']
        controls += [ colors.LIGHT_RED, "Movement with 'vi' keys:\n",

                     colors.GREEN, " H", colors.WHITE, ": left", 
                     colors.GREEN, "    L", colors.WHITE, ": right", 
                     colors.GREEN, "    J", colors.WHITE, ": down", 
                     colors.GREEN, "      K", colors.WHITE, ": up\n",

                     colors.GREEN, " Y", colors.WHITE, ": up-left", 
                     colors.GREEN, " U", colors.WHITE, ": up-right", 
                     colors.GREEN, " B", colors.WHITE, ": down-left", 
                     colors.GREEN, " N", colors.WHITE, ": down-right\n"]

        controls += [ colors.LIGHT_RED, "Movement with num-pad:\n",

                     colors.GREEN, " 4", colors.WHITE, ": left", 
                     colors.GREEN, "    6", colors.WHITE, ": right", 
                     colors.GREEN, "    2", colors.WHITE, ": down", 
                     colors.GREEN, "      8", colors.WHITE, ": up\n",

                     colors.GREEN, " 7", colors.WHITE, ": up-left", 
                     colors.GREEN, " 9", colors.WHITE, ": up-right", 
                     colors.GREEN, " 1", colors.WHITE, ": down-left", 
                     colors.GREEN, " 3", colors.WHITE, ": down-right\n", colors.WHITE, '\n']
        controls += [ colors.GREEN, "Left click ", colors.WHITE, "to move to location\n"]
        controls += [ colors.GREEN, "Right click ", colors.WHITE, "to move and dig to location\n", colors.WHITE, '\n']
        controls += [ colors.GREEN, "I ", colors.WHITE, "for inventory\n"]
        controls += [ colors.GREEN, "A ", colors.WHITE, "for abilities\n"]
        controls += [ colors.GREEN, "C ", colors.WHITE, "for this menu (controls)\n"]
        menus.msgbox(controls, width=60)
        return False

    def has_action(self, key, mouse):
        assert self.action == None # Did we handle the last action ? 

        dir = globals.key2direction(key)
        if dir:
            return self.queue_move(dir[0], dir[1])
        elif key.c == ord('i'):
            return self.handle_inventory()
        elif key.c == ord('c'):
            return self.handle_controls()
        elif key.c == ord('a'):
            return self.handle_abilities()
        elif key.c == ord('q'):
            self.goto_next_level()
            return self.queue_move(0,0)
        elif key.c == ord('m'):
            for obj in globals.world.level.objects_at(self.xy):
                if type(obj) == Resource:
                    obj.waypoint = True
            return False
        elif self.handle_clicks(mouse):
            return True

        return False

    def print_stats(self):
        import gui
        from globals import panel, world

        if self.stats.hp > 0:
            gui.render_bar( Pos(3,3), 20, "HP", int(self.stats.hp), self.stats.max_hp, colors.RED, colors.DARK_GRAY )
            gui.render_bar( Pos(3,4), 20, "MP", int(self.stats.mp), self.stats.max_mp, colors.BLUE, colors.DARK_GRAY )
        gui.render_bar( Pos(3,5), 20, "Harvest", self.points, world.level.points_needed, colors.DARK_GREEN, colors.DARK_GRAY )

        self.stats.inventory.draw(panel, INVENTORY_LOCATION_IN_PANEL)
        self.stats.statuses.draw(panel, Pos(3, 6))

        item_slot = _get_mouse_item_slot(self, libtcod.mouse_get_status())

        print_colored(panel, Pos(3, 0), colors.BABY_BLUE, 'BUGHACK  ')
        print_colored(panel, Pos(3, 2), 
                      colors.WHITE, 'Level ', colors.YELLOW, str(world.level.level_index+1)+" ",
                      colors.WHITE, 'Rank ', colors.YELLOW, self.rank )

        print_colored(panel, Pos(3, 1), colors.GOLD, 'A', colors.WHITE, 'bilities')
        print_colored(panel, Pos(14, 1), colors.GOLD, 'C', colors.WHITE, 'ontrols')

        if not item_slot:
            world.messages.draw(panel, Pos(33, 0))
        else:
            print_colored(panel, Pos(33, 0), colors.MUTED_GREEN, item_slot.item_type.name)
            print_colored(panel, Pos(34, 1), colors.YELLOW, item_slot.item_type.summary)
            print_colored(panel, Pos(34, 3), colors.BABY_BLUE, "Left click to use")
            print_colored(panel, Pos(34, 4), colors.WHITE, "Right click to drop")
