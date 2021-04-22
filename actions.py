from __future__ import annotations  # future >= 3.10

from typing import Optional, Tuple, TYPE_CHECKING

# break circular import
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to"""
        return self.entity.gamemap.engine
    

    def perform(self) -> None:
        """
        Perform this action with the objects needed to determine its scope

        `self.engine` is the scope that the action is being performed in

        `self.entity` is the object performing the action
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this action's destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy
    
    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity, if any, at this action's destination"""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAttack(ActionWithDirection):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return

        print(f'You kick the {target.name}, vexing it')


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return  # destination is out of bounds
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            return  # destination tile is impassible
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return  # destination blocked by entity

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAttack(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
