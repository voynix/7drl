from __future__ import annotations

import collections
from collections import defaultdict
from typing import Dict, List, Optional, TYPE_CHECKING

import exceptions
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self._capacity = capacity
        # items stack in lists
        # so as to maintain unique properties of items that may be orthogonal to stacking
        self._items: collections.defaultdict[str, List[Item]] = defaultdict(list)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def contents(self) -> Dict[str, List[Item]]:
        return {name: items for name, items in self._items.items() if len(items) > 0}

    def item_stack(self, item_name: str) -> Optional[List[Item]]:
        if item_name in self._items:
            return self._items[item_name]
        return None

    def insert(self, item: Item, add_message: bool = True) -> None:
        """
        Insert an item into the inventory, respecting stacks, and raise if the inventory is full
        """
        if (
            not (item.name in self._items and item.stackable)
            and len(self._items) >= self.capacity
        ):
            raise exceptions.Impossible("Your inventory is full")

        item.parent = self

        self._items[item.name].append(item)
        # unfortunately, we can't remove the item from its current location
        # as we don't know how nested our parent is from the GameMap or other Inventory
        # that currently owns the item
        # so the caller must take care of this

        if add_message:
            self.engine.message_log.add_message(f"You pick up the {item.name}")

    def remove(self, item: Item) -> None:
        """
        Removes the item from the inventory. Does NOT handle reowning the item
        """
        self._items[item.name].remove(item)

    def drop(self, item: Item) -> None:
        """
        Remove an item from the inventory and restore it to the game map at the player's location
        """
        self.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You drop the {item.name}")
