from geometry import *

class MoveAction:
    def __init__(self, xy): 
        self.destination = xy
    def perform(self, actor):   
        actor.xy = self.destination

class AttackAction:
    def __init__(self, target): 
        self.target = target
    def perform(self, actor):   
        actor.attack(self.target)