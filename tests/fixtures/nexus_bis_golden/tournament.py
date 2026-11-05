"""Each opponent meets each other opponent exactly once."""

from ex3 import FlameFactory, TransformCreatureFactory
from ex3.factories import CreatureFactory
from ex4 import (AggressiveStrategy, BattleStrategy,
                 InvalidStrategyError, NormalStrategy)


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
            (TransformCreatureFactory(), AggressiveStrategy())])
    battle([(TransformCreatureFactory(), AggressiveStrategy()),
            (FlameFactory(), AggressiveStrategy())])
