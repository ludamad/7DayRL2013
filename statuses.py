import colors
from utils import *
from geometry import *

class StatusType:
    def __init__(self, name, add_action, remove_action, color=colors.GREEN, step_action=None, duration=None, remove_criteria=None):
        self.name = name
        self.add_action = add_action
        self.remove_action = remove_action
        self.color = color
        self.duration = duration
        self.step_action = step_action
        self.remove_criteria = remove_criteria

class Status:
    def __init__(self, type):
        self.type = type
        self.duration = type.duration
        self.removed = False
    def add(self, owner):
        self.type.add_action(owner)
    def remove(self, owner):
        if self.removed: 
            return
        self.type.remove_action(owner)
        self.removed = True
    def step(self, owner):
        if not self.removed and self.type.step_action:
            self.type.step_action(owner)

        if self.type.remove_criteria and self.type.remove_criteria(owner):
            self.remove(owner)
        elif self.duration:
            self.duration -= 1
            if self.duration <= 0:
                self.remove(owner)

class Statuses:
    def __init__(self):
        self.statuses = []
    def remove_status(self, owner, status_type):
        for status in self:
            if status.type == status_type:
                status.remove(owner)
        return None
    def has_status(self, status_type):
        for status in self:
            if status.type == status_type:
                return status
        return None
    def step(self, owner):
        for status in self: 
            status.step(owner)
        self.statuses = filter(lambda status: not status.removed, self.statuses)
    def add_status(self, owner, status_type):
        status = self.has_status(status_type)
        if status:
            status.duration = status_type.duration
        else:
            status = Status(status_type)
            status.add(owner)
            self.statuses.append(status)
    def __iter__(self):
        return iter(self.statuses)
    def __getitem__(self, idx):
        return self.statuses[idx]
    def draw(self, con, xy, max_to_draw = 3):
        i = 0
        for status in self:
            if status.type.name:
                xy = print_colored( con, xy, status.type.color, status.type.name + ' ' )
                i += 1
                if i >= max_to_draw: 
                    break

def gain_hp(user, hp):
    user.stats.regen_hp(hp)

def gain_mp(user, mp):
    user.stats.regen_hp(mp)

def change_maxhp(user, hp):
    user.stats.max_hp += hp

def change_attack(user, atk):
    user.stats.attack += atk

SUGAR_RUSH = StatusType(
        name = "Sugar Rush", 
        add_action = lambda user: change_attack(user, 10),
        remove_action = lambda user: change_attack(user, -10),
        duration=3+1, # Account for turn that its used in
)