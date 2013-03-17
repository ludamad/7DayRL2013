from geometry import *

class MoveAction:
    def __init__(self, xy): 
        self.destination = xy
    def perform(self, actor):
        from workerants import WorkerAnt
        from globals import world

        for obj in world.level.objects_at(self.destination):
            if isinstance(obj, WorkerAnt):
                obj.xy = actor.xy

        actor.xy = self.destination

class DigAction:
    def __init__(self, xy): 
        self.target = xy
    def perform(self, actor):
        from workerants import WorkerAnt
        from globals import world

        world.level.map[self.target].make_floor()

class AttackAction:
    def __init__(self, target): 
        self.target = target
    def perform(self, actor):
        actor.attack(self.target)

class UseItemAction:
    def __init__(self, item_slot):
        self.item_slot = item_slot
    def perform(self, actor):   
        actor.use_item(self.item_slot)

class DropItemAction:
    def __init__(self, item_slot):
        self.item_slot = item_slot
    def perform(self, actor):   
        actor.drop_item(self.item_slot)

class UseAbilityAction:
    def __init__(self, ability, target): 
        self.ability = ability
        self.target = target
    def perform(self, actor):
        self.ability.perform(actor, self.target)