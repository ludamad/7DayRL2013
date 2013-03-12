from gameobject import GameObject
from tiles import *
from geometry import *
from colors import *
from utils import *

class ItemType:
    def __init__(self, summary, tile, use_action, unwield_action=None):
        self.use_action = use_action
        self.tile = tile
        self.unwield_action = unwield_action
        self.summary = summary

class ItemSlot:
    def __init__(self, itemtype):
        self.item_type = itemtype

class Inventory:
    def __init__(self, max_items=10):
        self.items = []
        self.equipped = None
        self.max_items = max_items
    def add_item(self, item):
        self.items.append(ItemSlot(item))

    def use_item(self, user, itemslot):
        self.items.remove(itemslot)
        itemslot.item_type.use_action(self, user)

    def has_room(self):
        return len(self.items) < self.max_items

    def unequip_item(self, user):
        if self.equipped:
            self.equipped.unwield_action(self, user)
            self.equipped = None

    def equip_item(self, user, itemslot):
        self.items.remove(itemslot)
        self.unequip_item(user)
        self.equipped = itemslot.item_type
    def draw(self, con, xy, max_slots=10):
        for i in range(max_slots):
            draw_xy = xy + Pos( i%5, i%2 )
            
            print_colored(con, xy - Pos(0,1), GOLD, 'I', WHITE, 'tems')
            color = [Color(0, 30, 0), Color(0,70,0)][(i%2+i%5)%2]
            con.put_char_ex(draw_xy, ' ', color, color)
            if i < len(self.items):
                tt = self.items[i].item_type.tile
                tt.variant(0).draw( con, draw_xy, True, color)

class ItemObject(GameObject):
    def __init__(self, xy, item_type=None, on_pickup=None):
        GameObject.__init__(self, xy, item_type.tile, solid=False, draw_once_seen=True)
        if item_type:
            def on_pickup(player, _):
                player.add_item(item_type)
            self.on_pickup = on_pickup
            self.is_inv_item = True
        else:
            self.on_pickup = on_pickup
            self.is_inv_item = False
            
    def step(self):
        from player import Player
        from globals import world

        for obj in world.level.objects_at(self.xy):
            if isinstance(obj, Player):
                if not self.is_inv_item or obj.stats.inventory.has_room():
                    self.on_pickup(obj, self)
                    world.level.queue_removal(self)
                return
            
# HERE BE ITEM DATA

def gain_hp(user, hp):
    user.stats.regen_hp(hp)

def change_maxhp(user, hp):
    user.stats.max_hp += hp

HEALING_FOOD = ItemType(
        summary = "Heals 25 HP",
        tile = TileType(
            # ASCII mode
             { "char" : '@', "color" : PALE_RED },
            # Tile mode
             { "char" : tile(3,1)}
        ),
        use_action = lambda user, inv: gain_hp(user, 25)
)