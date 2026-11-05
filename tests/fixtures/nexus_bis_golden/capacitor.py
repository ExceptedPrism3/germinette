"""Exercise the transform capability of both family members."""
from ex3 import TransformCreatureFactory
from ex3.capabilities import TransformCapability


if __name__ == '__main__':
    factory = TransformCreatureFactory()
    for entity in (factory.create_base(), factory.create_evolved()):
        print(entity.describe(), entity.attack())
        if isinstance(entity, TransformCapability):
            print(entity.transform(), entity.attack(), entity.revert())
