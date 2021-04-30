from components.ai import HostileEnemy
from components.consumable import ConfusionConsumable, FireballDamageConsumable, HealingConsumable, LightningDamageConsumable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

PLAYER = Actor(char='@', color=(255, 255, 255), name='Player', ai_cls=HostileEnemy, fighter=Fighter(hp=30, defense=2, power=5), inventory=Inventory(capacity=26), level=Level(level_up_base=200))

ORC = Actor(char='o', color=(63, 127, 63), name='Orc', ai_cls=HostileEnemy, fighter=Fighter(hp=10, defense=0, power=3), inventory=Inventory(capacity=0), level=Level(xp_given=35))
TROLL = Actor(char='T', color=(0, 127, 0), name='Troll', ai_cls=HostileEnemy, fighter=Fighter(hp=16, defense=1, power=4), inventory=Inventory(capacity=0), level=Level(xp_given=100))

CONFUSION_SCROLL = Item(char='~', color=(207, 63, 255), name='Confusion Scroll', consumable=ConfusionConsumable(number_of_turns=10))
FIREBALL_SCROLL = Item(char='~', color=(255, 0, 0), name='Fireball Scroll', consumable=FireballDamageConsumable(damage=12, radius=3))
HEALTH_POTION = Item(char='!', color=(127, 0, 255), name='Health Potion', consumable=HealingConsumable(amount=4))
LIGHTNING_SCROLL = Item(char='~', color=(255, 255, 0), name='Lightning Scroll', consumable=LightningDamageConsumable(damage=20, maximum_range=5))
