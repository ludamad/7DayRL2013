from geometry import *

class MoveAction:
    def __init__(self, xy): 
        self.destination = xy
    def perform(self, actor):   
        #trail immediately before leaving a square
        actor.trail();
        actor.xy = self.destination

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