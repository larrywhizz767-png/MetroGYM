---
icon: lucide/database
---

# Saving and Loading Worlds

`MetroSystem` can persist its declarative pipeline to disk, load it again later, and then either re-run the same world or extend it with new primitives before fitting.

!!! tip "What gets saved"
    `save()` stores the system configuration and the declared pipeline steps.
    It does not store transient runtime state such as the current tick, collision history, or a fitted simulator.

## Concept

The MetroGYM workflow still has the same three phases:

```text
MetroSystem(...)
  -> pipeline([...])
  -> save("world.pkl")
  -> MetroSystem.load("world.pkl")
  -> pipeline([...existing steps..., more primitives...])
  -> fit()
  -> run() / step(n)
```

This matters because persistence works at the world-definition level, not at the live-runtime level. A loaded system comes back as a fresh, unfitted `MetroSystem`, so you can:

- rebuild the same world exactly;
- inspect or modify the declared steps;
- add more trains, signals, or renderer primitives on top of the loaded world;
- call `fit()` again to materialise a new runtime.

## Minimal Example

```python
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Stored Loop", tick_ms=300).pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
        Station("East", (420, 120)),
        Station("South", (420, 320)),
    ]),
    Train("A", line="Loop", solver=train.always_hold()),
])

system.save("stored_loop.pkl")

loaded = MetroSystem.load("stored_loop.pkl")
loaded.fit().run()
```

The call to `save("stored_loop.pkl")` writes a pickle file containing the public `MetroSystem` configuration and the pipeline steps. `MetroSystem.load(...)` reconstructs the declarative world, but does not auto-fit it. That final `fit()` call is still the build boundary.

## Extending a Loaded World

Loading is useful when one world should become the base layer for another. The loaded object exposes the same `steps` list as any freshly declared system, so you can rebuild the pipeline with additional primitives.

```python
from metrogym import MetroSystem, train
from metrogym.primitives import Train

loaded = MetroSystem.load("stored_loop.pkl")

loaded.pipeline([
    *loaded.steps,
    Train("B", line="Loop", start_at=50, solver=train.always_proceed()),
])

loaded.fit().step(25)
```

In this pattern, `*loaded.steps` keeps the saved infrastructure and existing rolling stock, whilst the new `Train(...)` is appended on top. The result is a new world declaration derived from the saved one.

## What Can Go Wrong

!!! warning "Pickle compatibility"
    `save()` uses Python's built-in `pickle` module. If a custom solver or helper object inside the pipeline cannot be pickled, saving will fail with a `TypeError`.

!!! warning "Use a pickle extension"
    `MetroSystem.save()` expects a path ending in `.pkl` or `.pickle`.

## Where Next?

If you want to understand the structure of the saved world before extending it, return to [Building worlds](building-worlds.md). If you want to inspect every public method on the facade, see the [MetroSystem API reference](../API/foundations/metro-system.md).
