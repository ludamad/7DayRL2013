import console
from geometry import *
from colors import *
import libtcodpy as libtcod
from utils import *
from tiles import tile, TileType

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

def draw_pointer_func(char =('*','*'), good_color=YELLOW, bad_color=RED, radius = 0):
    def _draw_pointer(con, xy, valid):
        con.set_default_background(LIGHT_GRAY)
        from globals import ASCII_MODE, on_screen
        color = ( WHITE if not ASCII_MODE else good_color) if valid else bad_color
        con.set_default_foreground(color)
        points = [ xy + Pos(x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
        for pxy in points:
            con.put_char(on_screen(pxy), char[0] if ASCII_MODE else char[1], libtcod.BKGND_MULTIPLY)

    return _draw_pointer

def _line_no_solid(from_xy, to_xy):
    from globals import world

    for x, y in libtcod.line_iter(from_xy.x, from_xy.y, to_xy.x, to_xy.y):
        if world.level.map[Pos(x,y)].blocked:
            return False

    return True

MAX_RADIUS=10
def choose_location(user, validity_func, radius=None, fail_message=None, guess_target = True, draw_pointer=draw_pointer_func() ):
    from globals import game_blit, effects, screen, key2direction, world, SCREEN_SIZE, on_screen

    # Pick random valid
    
    target_xy = user.xy
    if guess_target:
        valid_candidates = []
        for xy in make_rect(Pos(0,0), world.level.size).xy_values():
            if xy.distance(user.xy) < radius and validity_func(user, xy):
                valid_candidates.append(xy)
        if valid_candidates:
            target_xy = valid_candidates[rand(0, len(valid_candidates)-1)]

    while True:
        game_blit(False)

        valid = validity_func(user, target_xy)

        effects.clear()
        if radius:
            for xy in world.view.xy_values():
                if xy.distance(user.xy) < radius:
                    effects.set_char_background(on_screen(xy), screen.get_char_background(xy))

        effects.blit( make_rect(Pos(0,0), SCREEN_SIZE), screen, Pos(0,0), 0.0, 0.7)

        draw_pointer(screen, target_xy, valid)
        screen.flush()

        key, mouse = libtcod.Key(), libtcod.Mouse()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        dir = key2direction(key)

        new_xy = target_xy
        if key.vk == libtcod.KEY_ENTER:
            if valid:
                return target_xy
            elif fail_message: 
                fail_message(target_xy)
                
        elif dir:
            new_xy = target_xy + Pos(dir[0], dir[1])
        elif key.pressed:
            return None
        elif mouse.lbutton_pressed:
            new_xy = Pos(mouse.cx, mouse.cy)
            print new_xy
            if new_xy == target_xy:
                if valid:
                    return target_xy
                elif fail_message: 
                    fail_message(target_xy)

        if world.level.map.valid_xy(new_xy):
            target_xy = new_xy


def _target_object_type(user, radius, 
                        can_target_through_solids=True, object_criteria=None, 
                        object_type=None, guess_target=True, 
                        draw_pointer=draw_pointer_func() ):
    from globals import world

    def valid_shot(user, xy):
        from globals import world

        if xy.distance(user.xy) >= radius or not world.fov.is_visible(xy): 
            return False
        if not object_criteria and not object_type:
            if world.level.map[xy].blocked or any(world.level.objects_at(xy)): 
                return False

        has_object = not object_type and not object_criteria
        for obj in world.level.objects_at(xy):
            if not object_type or isinstance(obj, object_type):
                if not object_criteria or object_criteria(obj):
                    has_object = True
                    break
        if not has_object:
            return False
        if not can_target_through_solids and not _line_no_solid(user.xy, xy): 
            return False

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

### COMBAT ABLIITIES ###

def spit():
    from enemies import Enemy

    return Ability(
        name = 'Spit',
        summary = 'Do 10 damage to an enemy from a short range',
        perform_action = lambda user, xy: _damage_at(user, xy, 10, "You spit at the %%!"),
        target_action = lambda user: _target_object_type(user, 3, 
                                                         object_type=Enemy,
                                                         draw_pointer = draw_pointer_func( char = ('*', tile(4,8)) ) ),
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
                                                         draw_pointer = draw_pointer_func(radius=1, char = ('*', tile(5,8)) )),
        mana_cost = 25,
        cooldown = 5
    )

def mutant_thorns():
    from enemies import Enemy

    return Ability(
        name = 'Thorns',
        summary = 'Do 20 damage to an enemy from a distance',
        perform_action = lambda user, xy: _damage_at(user, xy, 20, "You impale the %%!", 
                                                        radius=0),
        target_action = lambda user: _target_object_type(user, 5, 
                                                         object_type=Enemy,
                                                         can_target_through_solids = False,
                                                         draw_pointer = draw_pointer_func(bad_color=ORANGE, char=('^', tile(8,7)) )),
        mana_cost = 25,
        cooldown = 10
    )

### NON COMBAT ABLIITIES ###

def call_ants():
    from enemies import Enemy
    from workerants import WorkerAntHole, WorkerAnt

    def _spawn_ant_worker(user, xy):
        from globals import world
        for obj in world.level.objects_at(xy):
            if isinstance(obj, WorkerAntHole):
                obj.start_spawning()
                break
        world.messages.add( [PALE_RED, "The ants come marching!"] )

    def _ant_hole_criteria(anthole):
        return not anthole.spawning

    return Ability(
        name = 'Call Ants',
        summary = 'Call forth harvesting ants from an ant-hole',
        perform_action = _spawn_ant_worker,
        target_action = lambda user: _target_object_type(user, 9,
                                                         object_criteria=_ant_hole_criteria,
                                                         object_type=WorkerAntHole,
                                                         draw_pointer = draw_pointer_func(char=('a', tile(8,8)) )),
        mana_cost = 5,
        cooldown = 35
    )


BAD_SMELL = TileType(    
         { "char" : '#', "color" : RED }, # ASCII mode
         { "char" : tile(10,8) }  # Tile mode
)
def bad_smell():
    from enemies import Enemy
    from workerants import WorkerAntHole, WorkerAnt
    from scents import ScentObject

    def _spawn_scent(user, xy):
        from globals import world
        world.level.add_to_front_of_combatobjects(ScentObject(xy, BAD_SMELL, -100))
        world.messages.add( [PALE_YELLOW, "You create a pungent cloud!"] )

    return Ability(
        name = 'Bad Smell',
        summary = 'Dissuades your workers from wandering somewhere',
        perform_action = _spawn_scent,
        target_action = lambda user: _target_object_type(user, 9,
                                                         guess_target=False,
                                                         draw_pointer = draw_pointer_func(char=('#', tile(10,8)) )),
        mana_cost = 10,
        cooldown = 0
    )

def paralyze():
    from enemies import Enemy
    from globals import world
    from workerants import WorkerAntHole, WorkerAnt
    from scents import ScentObject
    from statuses import PARALYZE

    def _paralyze(user, xy):
        radius=2
        points = [ xy + Pos(x,y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) ]
        for pxy in points:
            for obj in world.level.objects_at(pxy):
                if isinstance(obj, Enemy):
                    obj.add_status(PARALYZE)
                    world.messages.add( [ BABY_BLUE, "You paralyze the " + obj.name +"!"])
                    break

    return Ability(
        name = 'Paralyze',
        summary = 'Stop enemies from doing anything for a while.',
        perform_action = _paralyze,
        target_action = lambda user: _target_object_type(user, 8, 
                                                         guess_target=False,
                                                         can_target_through_solids = False, 
                                                         draw_pointer = draw_pointer_func(radius=2, char = (chr(231), tile(8,6)) )),
        mana_cost = 10,
        cooldown = 0
    )
        
        
def blink():
    from enemies import Enemy
    from workerants import WorkerAntHole, WorkerAnt

    def _blink(user, xy):
        from globals import world
        world.messages.add( [PALE_YELLOW, "You spontaneously translocate!"] )
        user.xy = xy

    return Ability(
        name = 'Blink',
        summary = 'Move from one point to another instantaneously',
        perform_action = _blink,
        target_action = lambda user: _target_object_type(user, 9,
                                                         guess_target=False,
                                                         draw_pointer = draw_pointer_func(char=('@', tile(8,8)) )),
        mana_cost = 10,
        cooldown = 0
    )