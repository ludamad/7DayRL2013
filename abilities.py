import console
from geometry import *
from colors import *
import libtcodpy as libtcod

class Ability:
    def __init__(self, name, summary, perform_action, target_action = None, mana_cost=0, cooldown=0):
        self.name = name
        self.summary = summary

        self.perform_action = perform_action
        self.target_action = target_action

        self.mana_cost = mana_cost
        self.cooldown = cooldown

        self.remaining_cooldown = 0

    def step(self):
        self.remaining_cooldown = max(self.remaining_cooldown - 1, 0)

    def perform(self, user):
        if self.target_action:
            target = self.target_action(user)
            if not target:
                return False
            self.perform_action(user, target)
            self.remaining_cooldown = self.cooldown
        else:
            self.perform_action(user)
            self.remaining_cooldown = self.cooldown
        return True

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

MAX_RADIUS=10
def choose_location(user, validity_func):
    from globals import game_blit, screen, key2direction, world
    target_xy = user.xy
    while True:
        key = console.wait_for_keypress(True)
        game_blit(False)

        valid = validity_func(user, target_xy)

        screen.put_char(target_xy, '*', colors.YELLOW if valid else colors.RED , libtcod.BKGND_MULTIPLY)
        screen.flush()

        key, mouse = libtcod.Key(), libtcod.Mouse()
        libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        dir = key2direction(key)

        new_xy = target_xy
        if valid and key.vk == libtcod.KEY_ENTER:
            return target_xy
        elif dir:
            new_xy = target_xy + Pos(dir[0], dir[1])
        elif key.pressed:
            return None
        elif mouse.pressed:
            new_xy = Pos(mouse.cx, mouse.cy)
            if valid and new_xy == target_xy:
                return target_xy

        if world.level.map.valid_xy(new_xy):
            target_xy = new_xy


def _target_object_type(user, radius, object_type):
    from globals import world

    def valid_shot(user, xy):
        has_enemy = any( isinstance(obj, object_type) for obj in world.level.objects_at(xy) )
        return user.distance(xy) < radius and has_enemy

    return choose_location(user, valid_shot)

def _damage_enemy_at(user, xy, damage, log_message):
    from globals import world
    from enemies import Enemy

    for obj in world.level.objects_at(xy):
        if isinstance(obj, Enemy):
            world.messages.add(BABY_BLUE, log_message.replace('%%', obj.name))
            obj.damage(user, damage)
            return

def spit():
    from enemies import Enemy

    return Ability(
        name = 'Spit',
        summary = 'Do 10 damage to an enemy from a short range.',
        perform_action = lambda user, xy: _damage_enemy_at(user, xy, 10, "You spit at the %%!"),
        target_action = lambda user: _target_object_type(user, 2, Enemy),
        mana_cost = 10,
        cooldown = 2
    )