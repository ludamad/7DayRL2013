from geometry import *

class MoveAction:
    def __init__(self, xy): 
        self.destination = xy
    def perform(self, actor):   
        actor.xy = self.destination
