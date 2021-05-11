from components.ai import HostileEnemy
from components.consumable import (
    ConfusionConsumable,
    FireballDamageConsumable,
    HealingConsumable,
    LightningDamageConsumable,
)
from components.equipment import Equipment
from components.equippable import Dagger, Sword, LeatherArmor, ChainMail
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

PLAYER = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)

ORC = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
TROLL = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)

DAGGER = Item(char="/", color=(0, 191, 255), name="Dagger", equippable=Dagger())
SWORD = Item(char="/", color=(0, 191, 255), name="Sword", equippable=Sword())
LEATHER_ARMOR = Item(
    char="[", color=(139, 69, 19), name="Leather Armor", equippable=LeatherArmor()
)
CHAIN_MAIL = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=ChainMail()
)

CONFUSION_SCROLL = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=ConfusionConsumable(number_of_turns=10),
)
FIREBALL_SCROLL = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=FireballDamageConsumable(damage=12, radius=3),
)
HEALTH_POTION = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=HealingConsumable(amount=4),
)
LIGHTNING_SCROLL = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=LightningDamageConsumable(damage=20, maximum_range=5),
)
