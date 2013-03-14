from gameobject import GameObject
from items import Inventory
from abilities import Abilities
from statuses import Statuses

class CombatStats:
    def __init__(self, hp=0, hp_regen=0, mp =0, mp_regen = 0, attack = 0):
        self.hp = hp
        self.max_hp = hp
        self.hp_regen = hp_regen

        self.mp = mp
        self.max_mp = mp
        self.mp_regen = mp_regen

        self.attack = attack

        self.inventory = Inventory()
        self.abilities = Abilities()
        self.statuses = Statuses()

    def step(self, owner):
        self.regen_hp(self.hp_regen)
        self.regen_mp(self.mp_regen)
        self.abilities.step()
        self.statuses.step(owner)

    def regen_hp(self, amount):
        self.hp = min(self.hp+amount, self.max_hp)

    def regen_mp(self, amount):
        self.mp = min(self.mp+amount, self.max_mp)

class CombatObject(GameObject):
    def __init__(self, xy, tiletype, stats): 
        GameObject.__init__(self, xy, tiletype)
        self.stats = stats
    def attack(self, enemy):
        enemy.take_damage(self, self.stats.attack)
    def take_damage(self, attacker, damage):
        self.stats.hp = max(0, self.stats.hp - damage)
        if self.stats.hp <= 0:
            self.die()
    def step(self):
        self.stats.step(self)
    def die(self):
        raise "Not implemented!"

    def remove_status(self, status_type):
        self.stats.statuses.remove_status(self, status_type)
    def has_status(self, status_type):
        return self.stats.statuses.has_status(status_type)
    def add_status(self, status_type):
        self.stats.statuses.add_status(self, status_type)

    def trail(self):
        from globals import world
        world.level.scents.trail(self.xy)

    def add_item(self, item_type):
        self.stats.inventory.add_item(item_type)
    def use_item(self, item_slot):
        self.stats.inventory.use_item(self, item_slot)
    def drop_item(self, item_slot):
        self.stats.inventory.drop_item(self, item_slot)
    def unequip_item(self, user):
        self.stats.inventory.unequip_item(user)
    def equip_item(self, user, itemslot):
        self.stats.inventory.unequip_item(user, itemslot)
