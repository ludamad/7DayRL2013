

class Scents:
    def __init__(self):
        #map type of scent to the scent object
        self.scents = {}
    def add(self,type,scent):
        if self.scents[type]:
            self.scents[type].add(scent)
        else:
            self.scents[type] = scent
    def decay(self):
        for s in self.scents:
            s.decay()
        

class Scent:
    def __init__(self):
        self.strength = 0
        self.radius = 0
        self.decay = 0
    def add(self,scent):
        self.strength = self.strength + scent.strength
        self.radius = max(self.radius, scent.radius)
        self.decay = (self.decay + scent.decay) / 2.0        
    def decay(self):
        self.strength = self.strength - self.decay
        if self.strength < 0:
            self.strength = 0
        