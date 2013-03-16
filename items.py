from gameobject import GameObject
from tiles import *
from geometry import *
from colors import *
from utils import *
from statuses import *
from abilities import *

class ItemType:
    def __init__(self, name, summary, tile, use_action, can_use=None,unwield_action=None):
        self.name = name
        self.use_action = use_action
        self.tile = tile
        self.unwield_action = unwield_action
        self.summary = summary
        self.can_use = can_use

class ItemSlot:
    def __init__(self, itemtype):
        self.item_type = itemtype

class Inventory:
    def __init__(self, max_items=10):
        self.items = []
        self.equipped = None
        self.max_items = max_items
        self.target = None # a hack
    def add_item(self, item):
        self.items.append(ItemSlot(item))

    def use_item(self, user, item_slot):
        if item_slot.item_type.can_use and item_slot.item_type.can_use(self, user):
            self.items.remove(item_slot)
            item_slot.item_type.use_action(self, user)

    def drop_item(self, user, item_slot):
        from globals import world
        self.items.remove(item_slot)
        itemobject = ItemObject(user.xy, item_slot.item_type, dropped_this_turn=True)
        world.level.add(itemobject)

    def has_room(self):
        return len(self.items) < self.max_items

    def unequip_item(self, user):
        if self.equipped:
            self.equipped.unwield_action(self, user)
            self.equipped = None

    def equip_item(self, user, item_slot):
        self.items.remove(item_slot)
        self.unequip_item(user)
        self.equipped = item_slot.item_type

    def draw(self, con, xy):
        for i in range(self.max_items):
            draw_xy = xy + Pos( i%5,(i%2+i%5)%2 )
            
            print_colored(con, xy - Pos(0,1), GOLD, 'I', WHITE, 'tems')
            color = [Color(0, 30, 0), Color(0,70,0)][i%2]
            con.put_char_ex(draw_xy, ' ', color, color)
            if i < len(self.items):
                tt = self.items[i].item_type.tile
                tt.variant(0).draw( con, draw_xy, True, color)

    def find_clicked_item(self, xy):
        for i in range(len(self.items)):
            slot_xy = Pos( i%5, i%2 )
            if slot_xy == xy:
                return self.items[i]
        return None

class ItemObject(GameObject):
    def __init__(self, xy, item_type=None, pickup_description=None, on_pickup=None, dropped_this_turn=False):
        GameObject.__init__(self, xy, item_type.tile, solid=False, draw_once_seen=True)
        self.dropped_this_turn = dropped_this_turn
        self.item_type = item_type
        if item_type:
            if not pickup_description:
                self.pickup_description = (BABY_BLUE, "You pick up the ", WHITE, item_type.name, BABY_BLUE, ".")
            def on_pickup(player, _):
                player.add_item(item_type)
            self.on_pickup = on_pickup
        else:
            self.pickup_description = pickup_description
            self.on_pickup = on_pickup
            self.is_inv_item = False

    def step(self):
        from player import Player
        from globals import world

        if not self.dropped_this_turn:
            for obj in world.level.objects_at(self.xy):
                if isinstance(obj, Player):
                    if not self.item_type or obj.stats.inventory.has_room():
                        self.on_pickup(obj, self)
                        if self.pickup_description:
                            world.messages.add(self.pickup_description)
                        world.level.queue_removal(self)
                    else:
                        world.messages.add([LIGHT_GRAY, "There's a ", BABY_BLUE, self.item_type.name, LIGHT_GRAY, " but you can't hold it."])
                    return
        self.dropped_this_turn = False
            
# HERE BE ITEM DATA

APPLE_CHUNK = ItemType(
        name = "Apple Chunk",
        summary = "Heals 50 HP",
        tile = TileType(
            # ASCII mode
             { "char" : 248, "color" : PALE_RED },
            # Tile mode
             { "char" : tile(3,1)}
        ),
        use_action = lambda inv, user: gain_hp(user, 50)
)

ORANGE_CHUNK = ItemType(
        name = "Orange Chunk",
        summary = "Regains 50 MP",
        tile = TileType(
            # ASCII mode
             { "char" : 248, "color" : ORANGE },
            # Tile mode
             { "char" : tile(6,1)}
        ),
        use_action = lambda inv, user: gain_mp(user, 50)
)

def _use_watermelon(inv, user):
    from globals import world
    user.add_status(DEFENCE)
    world.messages.add([GREEN, "You gain defence!"])

WATERMELON_CHUNK = ItemType(
        name = "Watermelon Chunk",
        summary = "Your exoskeleton hardens for 10 turns",
        tile = TileType(
            # ASCII mode
             { "char" : 248, "color" : Color(232,34,62) },
            # Tile mode
             { "char" : tile(7,7)}
        ),
        use_action = _use_watermelon
)

def _use_jellybean(inv, user):
    from globals import world
    user.add_status(SUGAR_RUSH)
    world.messages.add([GREEN, "You're hyped from sugar!"])

JELLYBEAN = ItemType(
        name = "Jellybean",
        summary = "Do 10 more bite damage for the next 4 turns",
        tile = TileType(
            # ASCII mode
             { "char" : 236, "color" : PURPLE },
            # Tile mode
             { "char" : tile(11,7)}
        ),
        use_action = _use_jellybean
)

def _can_use_mushroom(inv, user):
    inv.target = paralyze().target(user)
    print inv.target
    return inv.target != None
    
def _use_mushroom(inv, user):
    from globals import world
    paralyze().perform(user, inv.target)
    inv.target = None

MUSHROOM = ItemType(
        name = "Mushroom",
        summary = "Paralyze enemies in a large radius",
        can_use = _can_use_mushroom,
        tile = TileType(
            # ASCII mode
             { "char" : 231, "color" : RED },
            # Tile mode
             { "char" : tile(8,6)}
        ),
        use_action = _use_mushroom
)

def _can_use_blinkgem(inv, user):
    inv.target = blink().target(user)
    print inv.target
    return inv.target != None
    
def _use_blinkgem(inv, user):
    from globals import world
    blink().perform(user, inv.target)
    inv.target = None

BLINKGEM = ItemType(
        name = "Blink Gem",
        summary = "Move from one point to another instantaneously",
        can_use = _can_use_blinkgem,
        tile = TileType(
            # ASCII mode
             { "char" : 229, "color" : GREEN },
            # Tile mode
             { "char" : tile(0,2)}
        ),
        use_action = _use_blinkgem
)