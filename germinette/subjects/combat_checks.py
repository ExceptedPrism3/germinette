"""Behavior contracts for the supplied factory/capability/strategy subjects."""

CLASSES = """
import importlib
import inspect
import pkgutil
import sys
from unittest.mock import patch

def classes(package):
    module = importlib.import_module(package)
    modules = [module]
    modules.extend(importlib.import_module(info.name) for info in
                   pkgutil.walk_packages(module.__path__, package + '.'))
    prefixes = tuple(package + '.' for package in PACKAGES)
    return {value for module in modules for value in vars(module).values()
            if inspect.isclass(value) and (value.__module__ in PACKAGES
                or value.__module__.startswith(prefixes))}

def noargs(call):
    try:
        inspect.signature(call).bind()
    except TypeError:
        print('Constructor or factory requires arguments; review manually.')
        sys.exit(77)
    return call()

entities = set().union(*(classes(package) for package in PACKAGES))
creatures = [cls for cls in entities if inspect.isabstract(cls)
             and 'attack' in cls.__abstractmethods__
             and callable(getattr(cls, 'describe', None))]
transforms = [cls for cls in entities if inspect.isabstract(cls)
              and {'transform', 'revert'} <= cls.__abstractmethods__]
healers = [cls for cls in entities if inspect.isabstract(cls)
           and 'heal' in cls.__abstractmethods__]
factory_bases = [cls for cls in entities if inspect.isabstract(cls)
                 and {'create_base', 'create_evolved'}
                 <= cls.__abstractmethods__]
assert creatures and factory_bases, 'Missing Creature or factory ABC'

def has_capability(entity, capabilities):
    return any(isinstance(entity, cls) for cls in capabilities)
"""

FACTORIES = CLASSES + """
package_classes = classes(PACKAGE)
factories = [cls for cls in package_classes
             if cls.__module__.startswith(PACKAGE)
             and not inspect.isabstract(cls)
             and any(issubclass(cls, base) for base in factory_bases)]
assert len(factories) >= 2, 'At least two concrete factories are required'
package = importlib.import_module(PACKAGE)
exported = {value for key, value in vars(package).items()
            if not key.startswith('_') and inspect.isclass(value)}
assert set(factories) <= exported, 'Expose the concrete factories'
assert not any(not inspect.isabstract(cls)
               and any(issubclass(cls, base) for base in creatures)
               for cls in exported), 'Do not expose concrete creatures'
if CAPABILITIES:
    assert transforms, 'Missing transform capability ABC'
    if HEALING:
        assert healers, 'Missing heal capability ABC'
    assert all(not issubclass(capability, creature)
               for capability in transforms + healers
               for creature in creatures)
products = []
for factory_cls in factories:
    factory = noargs(factory_cls)
    base = noargs(factory.create_base)
    evolved = noargs(factory.create_evolved)
    assert type(base) is not type(evolved), 'Need distinct base/evolved types'
    for entity in (base, evolved):
        assert any(isinstance(entity, creature) for creature in creatures)
        description = entity.describe()
        assert isinstance(description, str) and description
        before = entity.attack()
        assert isinstance(before, str) and before
        if CAPABILITIES and has_capability(entity, transforms):
            assert isinstance(entity.transform(), str)
            changed = entity.attack()
            assert isinstance(changed, str) and changed != before
            assert entity.attack() == changed, 'Transformation must persist'
            assert isinstance(entity.revert(), str)
            assert entity.attack() == before, 'Revert must restore the attack'
        if CAPABILITIES and has_capability(entity, healers):
            heal = entity.heal
            arguments = [entity] if inspect.signature(heal).parameters else []
            assert isinstance(heal(*arguments), str)
        products.append(entity)
if CAPABILITIES:
    assert any(has_capability(entity, transforms) for entity in products)
    if HEALING:
        assert any(has_capability(entity, healers) for entity in products)
    else:
        assert any(not has_capability(entity, transforms)
                   for entity in products)
"""

STRATEGIES = CLASSES + """
strategy_classes = classes(STRATEGY_PACKAGE)
strategy_bases = [cls for cls in strategy_classes if inspect.isabstract(cls)
                  and {'act', 'is_valid'} <= cls.__abstractmethods__]
assert strategy_bases, 'Missing strategy ABC'
factories = [cls for cls in entities if not inspect.isabstract(cls)
             and any(issubclass(cls, base) for base in factory_bases)]
products = [noargs(noargs(factory).create_base) for factory in factories]
plain = next((entity for entity in products
              if not has_capability(entity, transforms + healers)), None)
morph = next((entity for entity in products
              if has_capability(entity, transforms)), None)
healer = next((entity for entity in products
               if has_capability(entity, healers)), None)
assert plain is not None and morph is not None, 'Need plain/morph entities'
strategies = [noargs(cls) for cls in strategy_classes
              if not inspect.isabstract(cls)
              and any(issubclass(cls, base) for base in strategy_bases)]
normal = next((s for s in strategies if s.is_valid(plain) is True
               and s.is_valid(morph) is True
               and (not HEALING or s.is_valid(healer) is True)), None)
aggressive = next((s for s in strategies if s.is_valid(plain) is False
                   and s.is_valid(morph) is True
                   and (not HEALING or s.is_valid(healer) is False)), None)
assert normal is not None and aggressive is not None, 'Missing strategies'
pairs = [(normal, plain, ['attack']),
         (aggressive, morph, ['transform', 'attack', 'revert'])]
restricted = [aggressive]
if HEALING:
    assert healer is not None
    defensive = next((s for s in strategies if s.is_valid(plain) is False
                      and s.is_valid(morph) is False
                      and s.is_valid(healer) is True), None)
    assert defensive is not None, 'Missing defensive strategy'
    pairs.append((defensive, healer, ['attack', 'heal']))
    restricted.append(defensive)
for strategy in restricted:
    try:
        strategy.act(plain)
    except Exception as exc:
        assert type(exc).__module__ != 'builtins' and str(exc), (
            'Use a dedicated exception with a clear message')
    else:
        raise AssertionError('Invalid strategy combination must raise')
for strategy, entity, expected in pairs:
    events = []
    patches = []
    try:
        names = ['attack']
        if has_capability(entity, transforms):
            names += ['transform', 'revert']
        if has_capability(entity, healers):
            names += ['heal']
        for name in names:
            original = getattr(entity, name)
            def wrapper(*args, _name=name, _original=original, **kwargs):
                events.append(_name)
                return _original(*args, **kwargs)
            item = patch.object(entity, name, side_effect=wrapper)
            item.start()
            patches.append(item)
        strategy.act(entity)
    finally:
        for item in reversed(patches): item.stop()
    assert events == expected, (type(strategy).__name__, events, expected)
"""

DEMONSTRATION = """
import collections
import runpy
import sys
from pathlib import Path
counts = collections.Counter()
root = Path.cwd()
def profile(frame, event, arg):
    if event == 'call' and frame.f_code.co_name in REQUIRED:
        filename = Path(frame.f_code.co_filename)
        if filename.is_absolute() and root in filename.parents:
            counts[frame.f_code.co_name] += 1
sys.setprofile(profile)
try:
    runpy.run_path(SCRIPT, run_name='__main__')
finally:
    sys.setprofile(None)
for name, minimum in REQUIRED.items():
    assert counts[name] >= minimum, (SCRIPT, name, counts[name], minimum)
"""
