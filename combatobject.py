from gameobject import GameObject

class CombatStats:
    def __init__(self, hp, hp_regen, mp, mp_regen, attack):
        self.hp = hp
        self.max_hp = hp
        self.hp_regen = hp_regen
        self.mp = mp
        self.max_mp = mp
        self.mp_regen = mp_regen
        self.attack = attack
    def regen_for_step(self):
        self.hp = min(self.hp+0.1, self.max_hp)

class CombatObject(GameObject):
    def __init__(self, xy, tiletype, stats): 
        GameObject.__init__(self, xy, tiletype)
        self.stats = stats
    def attack(self, enemy):
        enemy.take_damage(self.stats.attack)
    def take_damage(self, damage):
        self.stats.hp = max(0, self.stats.hp - damage)
        if self.stats.hp <= 0:
            self.die()
    def die(self):
        raise "Not implemented!"
