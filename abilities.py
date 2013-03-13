import console
from geometry import *
from colors import *
import libtcodpy as libtcod
from utils import *

class Ability:
    def __init__(self, name, summary, perform_action, can_perform_action = None, target_action = None, mana_cost=0, cooldown=0):
        self.name = name
        self.summary = summary

        self.perform_action = perform_action
        self.target_action = target_action
        self.can_perform_action = can_perform_action

        self.mana_cost = mana_cost
        self.cooldown = cooldown

        self.remaining_cooldown = 0

    def step(self):
        self.remaining_cooldown = max(self.remaining_cooldown - 1, 0)

    def has_cooldown(self):
        return self.remaining_cooldown > 0
    def has_prereqs(self, user):
        can_perform = not self.can_perform_action or self.can_perform_action(user)
        return not self.has_cooldown() and self.mana_cost <= user.stats.mp and can_perform

    def target(self, user):
        from globals import world
        if self.mana_cost > user.stats.mp:
            world.messages.add( [PALE_RED, "Not enough mana to use ", BABY_BLUE, self.name, PALE_RED, "."] )
            return None
        if self.has_cooldown():
            world.messages.add( [PALE_RED, "You must wait before using ", BABY_BLUE, self.name, PALE_RED, " again."] )
            return None
        if self.can_perform_action and not self.can_perform_action(user):
            return None
        return not self.target_action or self.target_action(user)

    def perform(self, user, target):
        self.perform_action(user, target)
        user.stats.mp = max(0, user.stats.mp - self.mana_cost)
        self.remaining_cooldown = self.cooldown

class Abilities:
    def __init__(self):
        self.abilities = []
    def step(self):
        for ability in self.abilities:
            ability.step()
    def add(self, ability):
        self.abilities.append(ability)
    def __iter__(self):
        return iter(self.abilities)
    def __getitem__(self, idx):
        return self.abilities[idx]

def draw_pointer_func(char ='*', good_color=YELLOW, bad_color=RED, radius = 0):
    def _draw_pointer(con, xy, valid):
        con.set_default_background(LIGHT_GRAY)
        con.set_default_foreground(good_color if valid else bad_color)
        points = [ xy + Pos(x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
        for pxy in points:
            con.put_char(pxy, char, libtcod.BKGND_MULTIPLY)

    return _draw_pointer

def _line_no_solid(from_xy, to_xy):
    from globals import world

    for x, y in libtcod.line_iter(from_xy.x, from_xy.y, to_xy.x, to_xy.y):
        if world.level.map[Pos(x,y)].blocked:
            return False

    return True

MAX_RADIUS=10
def choose_location(user, validity_func, radius=None, guess_target = True, draw_pointer=draw_pointer_func() ):
    from globals import game_blit, effects, screen, key2direction, world, SCREEN_SIZE

    # Pick random valid
    
    target_xy = user.xy
    if guess_target:
        valid_candidates = []
        for xy in make_rect(Pos(0,0), SCREEN_SIZE).xy_values():
            if xy.distance(user.xy) < radius and validity_func(user, xy):
                valid_candidates.append(xy)
        if valid_candidates:
            target_xy = valid_candidates[rand(0, len(valid_candidates)-1)]

    while True:
        game_blit(False)

        valid = validity_func(user, target_xy)

        effects.clear()
        if radius:
            for xy in make_rect(Pos(0,0), SCREEN_SIZE).xy_values():
                if xy.distance(user.xy) < radius:
                    effects.set_char_background(xy, screen.get_char_background(xy))
        
        
        effects.blit( make_rect(Pos(0,0), SCREEN_SIZE), screen, Pos(0,0), 0.0, 0.7)

        draw_pointer(screen, target_xy, valid)
        screen.flush()

        key, mouse = libtcod.Key(), libtcod.Mouse()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        dir = key2direction(key)

        new_xy = target_xy
        if valid and key.vk == libtcod.KEY_ENTER:
            return target_xy
        elif dir:
            new_xy = target_xy + Pos(dir[0], dir[1])
        elif key.pressed:
            return None
        elif mouse.lbutton_pressed:
            new_xy = Pos(mouse.cx, mouse.cy)
            print new_xy
            if valid and new_xy == target_xy:
                return target_xy

        if world.level.map.valid_xy(new_xy):
            target_xy = new_xy


def _target_object_type(user, radius, can_target_through_solids=True, object_type=None, guess_target=True, draw_pointer=draw_pointer_func() ):
    from globals import world

    def valid_shot(user, xy):
        from globals import world
        if xy.distance(user.xy) >= radius: return False
        if not world.fov.is_visible(xy): return False
        has_object = not object_type or any( isinstance(obj, object_type) for obj in world.level.objects_at(xy) )
        if not has_object: return False
        if not can_target_through_solids and not _line_no_solid(user.xy, xy): return False
        return True

    return choose_location(user, valid_shot, radius,guess_target=guess_target, draw_pointer=draw_pointer)

def _damage_at(user, xy, damage, log_message, hurt_self=False, you_damage_message=None, radius=0):
    from globals import world
    from combatobject import CombatObject

    points = [ xy + Pos(x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
    for pxy in points:
        for obj in world.level.objects_at(pxy):
            if isinstance(obj, CombatObject):
                is_you = (obj == world.player)
                if hurt_self or not is_you:
                    world.messages.add( [BABY_BLUE if not is_you else RED, 
                                         log_message.replace('%%', obj.name) if not is_you else you_damage_message] )
                    obj.take_damage(user, damage)
                    break

def spit():
    from enemies import Enemy

    return Ability(
        name = 'Spit',
        summary = 'Do 10 damage to an enemy from a short range.',
        perform_action = lambda user, xy: _damage_at(user, xy, 10, "You spit at the %%!"),
        target_action = lambda user: _target_object_type(user, 3, object_type=Enemy),
        mana_cost = 10,
        cooldown = 0
    )

def acid_splash():
    from enemies import Enemy

    return Ability(
        name = 'Acid Ball',
        summary = 'Do 10 damage to enemies in a radius.',
        perform_action = lambda user, xy: _damage_at(user, xy, 10, "You splash the %% with acid!", 
                                                        hurt_self=True,
                                                        you_damage_message= "You splash yourself with acid!",
                                                        radius=1),
        target_action = lambda user: _target_object_type(user, 5, 
                                                         guess_target=False,
                                                         can_target_through_solids = False, 
                                                         draw_pointer = draw_pointer_func(radius=1)),
        mana_cost = 30,
        cooldown = 5
    )

def mutant_thorns():
    from enemies import Enemy

    return Ability(
        name = 'Thorns',
        summary = 'Do 20 damage to an enemy from a distance.',
        perform_action = lambda user, xy: _damage_at(user, xy, 20, "You impale the %%!", 
                                                        radius=1),
        target_action = lambda user: _target_object_type(user, 5, 
                                                         can_target_through_solids = False,
                                                         draw_pointer = draw_pointer_func(char='^')),
        mana_cost = 25,
        cooldown = 3
    )