"""Each opponent meets each other opponent exactly once."""

from ex0 import AquaFactory, CreatureFactory, FlameFactory
from ex1 import HealingCreatureFactory, TransformCreatureFactory
from ex2.strategies import (
    AggressiveStrategy, BattleStrategy, DefensiveStrategy,
    InvalidStrategyError, NormalStrategy,
)


def battle(opponents: list[tuple[CreatureFactory, BattleStrategy]]) -> None:
    print('*** Tournament ***')
    for index, (factory, strategy) in enumerate(opponents):
        for other_factory, other_strategy in opponents[index + 1:]:
            left, right = factory.create_base(), other_factory.create_base()
            print('* Battle *', left.describe(), 'vs.', right.describe())
            try:
                strategy.act(left)
                other_strategy.act(right)
            except InvalidStrategyError as exc:
                print('Battle error, aborting tournament:', exc)
                return


if __name__ == '__main__':
    battle([(FlameFactory(), NormalStrategy()),
            (HealingCreatureFactory(), DefensiveStrategy())])
    battle([(FlameFactory(), AggressiveStrategy()),
            (HealingCreatureFactory(), DefensiveStrategy())])
    battle([(AquaFactory(), NormalStrategy()),
            (HealingCreatureFactory(), DefensiveStrategy()),
            (TransformCreatureFactory(), AggressiveStrategy())])
