from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the appropriate action for this item"""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """
        Invoke this item's ability

        `action` is the context for this activation
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory"""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.remove(entity)


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        self.engine.message_log.add_message(
            "Select a target location", color.NEEDS_TARGET
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area you can't see")
        if not target:
            raise Impossible("You must select an enemy to target")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"You activate the {self.parent.name}. It shudders with mystic power."
        )
        self.engine.message_log.add_message(
            f"The {target.name} begins to stumble around with a vacant look in its eyes",
            color.STATUS_EFFECT_APPLIED,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns
        )
        self.consume()


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name} and recover {amount_recovered} HP",
                color.HEALTH_RECOVERED_TEXT,
            )
            self.consume()
        else:
            raise Impossible("You are already at full health")


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        self.engine.message_log.add_message(
            "Select a target location", color.NEEDS_TARGET
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")

        targets = []
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                targets.append(actor)
        if not targets:
            raise Impossible("There are no targets in the blast radius")

        self.engine.message_log.add_message(
            f"You activate the {self.parent.name}. It scorches your hand with mystic power."
        )
        for target in targets:
            self.engine.message_log.add_message(
                f"The {target.name} is engulfed in a fiery explosion and takes {self.damage} damage"
            )
            target.fighter.take_damage(self.damage)

        self.consume()


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 10

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"You activate the {self.parent.name}. It crackles with mystic power."
            )
            self.engine.message_log.add_message(
                f"A lightning bolt strikes the {target.name} with a loud thunder for {self.damage} damage",
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("There are no enemies close enough to strike")
