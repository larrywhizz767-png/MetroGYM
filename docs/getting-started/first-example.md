---
icon: lucide/braces
---

# First example

This first example follows the notation introduced in [Get started](index.md). Here, \(N\) is a simple loop network, \(T\) is a small set of trains, \(G\) is empty because no signals are introduced yet, and \(\Pi\) is the policy set attached to those trains.

It also uses the same pipeline workflow. You declare the world through `MetroSystem(...).pipeline([...])`, call `fit()` to validate and materialise it, and then execute it with `run()` or `step(n)`.

## Declaring and fitting a world

```python
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Basic: Simple Loop", tick_ms=400, render_scale=2).pipeline([
    Network([
        Line("Loop", Color(80, 200, 255), [(120, 120), (560, 120), (560, 380), (120, 380), (120, 120)]),
        Station("Origin", (120, 120)),
        Station("North", (560, 120)),
        Station("Far Side", (560, 380)),
        Station("West", (120, 380)),
    ]),
    Train("A", line="Loop", solver=train.always_hold(), asset="metro_nose"),
    Train("B", line="Loop", start_at=50, solver=train.always_hold(), asset="city_tram"),
])

system.fit().run()
```

This code defines the world first and executes it afterwards. In the notation above, the declared `Network(...)` provides \(N\), the two `Train(...)` objects provide \(T\), and the holding solvers provide \(\Pi\). Because no `Signal(...)` primitive appears in the pipeline, this example keeps \(G = \varnothing\). Calling `fit()` checks that the declared world is valid and builds the runtime objects. Calling `run()` then opens the simulation window and starts advancing the fitted world.

If you want to inspect the same world without opening a window, replace `run()` with `step(50)`. That advances the fitted simulation headlessly for a fixed number of ticks.

The public parameters are straightforward:

- `MetroSystem(name="Basic: Simple Loop", tick_ms=400, render_scale=2)` defines the overall simulation shell. The `name` becomes the window title, `tick_ms` sets the duration of one simulation tick in milliseconds, and `render_scale` enlarges the rendered scene.
- `Line("Loop", Color(80, 200, 255), [...])` defines the route geometry that trains follow. The string is the public line name, the colour sets the visual identity of the line, and the coordinate list defines the path itself.
- `Station("Origin", (120, 120))` defines a named station on the map. Each station is identified by a public name and a position.
- `Train("A", line="Loop", solver=train.always_hold(), asset="metro_nose")` defines a train, the line on which it runs, the runtime policy it follows, and optional rendering configuration. The second train adds `start_at=50`, which places it halfway along the same line.

## Changing the policy set

The previous example declares a world in which trains are present but inactive. The next step is to change \(\Pi\), that is, the policy set attached to the world. The simplest possible change is to replace the holding policy with a policy that always proceeds.

```python hl_lines="12"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Solver Basic: Always Run", tick_ms=400, render_scale=2).pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (560, 120), (560, 360), (120, 360), (120, 120)]),
        Station("Origin", (120, 120)),
        Station("North", (560, 120)),
        Station("South", (560, 360)),
        Station("West", (120, 360)),
    ]),
    Train("RUN", line="Loop", solver=train.always_proceed(), asset="metro_nose"),
])

system.fit().run()
```

Structurally, almost nothing changed: the same pipeline pattern is used, and the world is still built through `fit()` and executed through `run()`. The important difference is that \(\Pi\) now contains a movement policy rather than a holding policy. As a result, the same declarative world starts to evolve visibly once the simulation is running.

This is the main idea to carry forward: in `MetroGYM`, infrastructure and policies are separate objects. You can keep the same world and change only the decision rules, or keep the same decision rules and change only the world. That separation is what makes comparison meaningful.

Some train actions are directly available as typed decisions. `train.hold()` keeps the train stationary. `train.proceed()` allows it to continue forward at its current or default speed, whereas `train.proceed_at(speed)` continues forward at a specified target speed. `train.accelerate_to(speed)` increases speed towards a target value, and `train.brake_to(speed)` reduces speed towards one. `train.change_speed_by(delta)` adjusts the current target speed by a fixed amount, whilst `train.slow_down(delta=0.5)` reduces speed by a small default increment. Finally, `train.reverse()` sends the train in the opposite direction along the same line path.

For the built-in train policies and their composition helpers, see the [API reference for train solvers](../API/solvers/train-solvers.md).
