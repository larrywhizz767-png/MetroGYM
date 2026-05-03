# MetroGYM

Pure Python **pygame** MetroGYM library for teaching metro systems,
train control, signal control, graph search, and runtime architecture.
The installable `metrogym` package contains reusable library code; runnable
teaching scenes live in `examples/` and `challenges/`.

## Quick Start

From the repository root:

```bash
uv sync
uv run python examples/minimal.py
uv run python examples/demo.py
uv run python challenges/_smoke.py
```

## Canonical API

MetroGYM uses one primitive-first, scikit-learn-style construction path:

```python
from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train
from metrogym.rendering import MetroGYMRenderer

system = MetroSystem(name="My First Metro", tick_ms=400, render_scale=1).pipeline([
    Network([
        Line("Loop", Color(80, 200, 255), [
            (120, 120), (560, 120), (560, 380), (120, 380), (120, 120),
        ]),
        Station("Origin", (120, 120)),
        Station("Far Side", (560, 380)),
    ]),
    Train("A", line="Loop"),
    Train("B", line="Loop", start_at=50),
    Signal(
        "TL-Origin",
        (120, 120),
        controls=ControlRule("Loop", (120, 120), (560, 120)),
    ),
    MetroGYMRenderer(scale=1),
])

system.fit().run()
```

`MetroSystem(...)` owns runtime parameters. `.pipeline([...])` stacks public
primitives. `.fit()` validates and builds the runtime engine. `.run()` starts
the renderer, and `.step(n)` advances headlessly.

## Architecture

```text
src/metrogym/
  __init__.py
  system.py                         MetroSystem canonical pipeline facade
  context.py                        MetroContext shared build state
  runtimes.py                       runtime engine and RuntimeObject protocol
  controls.py                       ControlSystem and runtime SignalRule
  events.py                         passive event records such as CollisionEvent

  templates/
    primitive.py                    BaseMetroPrimitive fit/transform/params contract

  core/
    coordinates.py                  Position, PositionLike, Direction, coercion helpers
    colors.py                       ColorRGBA and Color palette/factory

  primitives/
    __init__.py                     public primitive exports
    network.py                      required Network aggregator
    line/
      line.py                       public Line primitive
      runtime.py                    RuntimeLine state
      control.py                    line-specific control hooks
      extras/path.py                path interpolation helpers
    station/
      station.py                    public Station primitive
      runtime.py                    RuntimeStation state
      control.py                    station-specific control hooks
    train/
      train.py                      public Train primitive
      runtime.py                    RuntimeTrain movement/collision logic
      control.py                    train-specific control hooks
    signal/
      signal.py                     public Signal primitive
      runtime.py                    RuntimeTrafficLight state
      control.py                    segment geometry helpers
      extras/control_rule.py        ControlRule config value object

  rendering/
    panel.py                        SimulationPanel scene container and tick loop
    _utils/gfx.py                   pygame.gfxdraw primitives, scaling, fonts
    _utils/keyboard.py              visualisation keyboard shortcuts
    primitives/metrogym_renderer/
      metrogym_renderer.py          public MetroGYMRenderer primitive
      runtime.py                    RuntimeMetroGYMRenderer drawing implementation
      extras/assets.py              asset/font paths
      extras/constants.py           renderer constants
```

Root-level teaching material:

```text
examples/                           runnable MetroGYM scenes
challenges/                         graph-search teaching challenges
  framework.py                      Graph/check/run helpers
  envs.py                           challenge graph fixtures
  solutions/                        instructor references
```

## Public Primitives

| Primitive | Purpose |
|---|---|
| `MetroSystem` | Owns runtime parameters, pipeline steps, validation, build, run lifecycle. |
| `Network` | Required aggregator for infrastructure primitives. |
| `Line` | Defines a named coloured path from waypoints. Must be inside `Network`. |
| `Station` | Defines a labelled station marker. Must be inside `Network`. |
| `Train` | Defines rolling stock attached to a line. `start_at=50` starts halfway along the path; same-line trains peer-check by default. |
| `Signal` | Defines a traffic signal and optional controlled segments. |
| `ControlRule` | Value object used inside `Signal(..., controls=...)`. |
| `MetroGYMRenderer` | Optional renderer primitive for renderer-level parameters such as `scale`. |

## Validation Rules

`fit()` validates the pipeline and runtime graph:

1. exactly one `Network(...)`;
2. `Line` and `Station` only inside `Network`;
3. at least one line;
4. at least one station;
5. at least one train;
6. no duplicate line names;
7. no duplicate station names;
8. no duplicate train IDs;
9. no duplicate signal IDs;
10. every train references an existing line;
11. every signal control references an existing line;
12. every signal control endpoint is on the referenced line path.

## Fit / Run Lifecycle

`fit()` performs the build and validation:

1. creates the internal runtime engine from `MetroSystem` parameters;
2. applies the `Network` infrastructure primitives;
3. applies train primitives;
4. applies signal/control primitives;
5. applies renderer configuration primitives;
6. auto-peers trains on the same line unless `peer_with_line=False`;
7. stores the build context and runtime simulator on the system.

`run()` starts the pygame loop. `step(n)` advances headlessly by `n` ticks.

## Train Collision Defaults

```python
Train("R1", line="Red")
Train("R2", line="Red", start_at=50)
```

Same-line trains are automatically linked for collision checks. Opt out per
train:

```python
Train("Maintenance", line="Red", peer_with_line=False)
```

## Signal Controls

A signal can control one or more line segments:

```python
Signal(
    "TL-North",
    position=(200, 80),
    period_ticks=4,
    controls=ControlRule("Red", start=(60, 80), end=(540, 80)),
)
```

If the signal is red, trains cannot enter the controlled segment. Trains already
inside the segment continue through.

Multiple controls:

```python
Signal(
    "Central Box",
    position=(300, 270),
    controls=[
        ControlRule("Red", (540, 140), (60, 140)),
        ControlRule("Blue", (200, 50), (200, 350)),
    ],
)
```

## Runtime Controls

While a pygame window is open:

| Shortcut | Action |
|---|---|
| `Ctrl+R` | Restart from tick 0. |
| `Ctrl+-` | Jump backward by 5% of current ticks. |
| `Ctrl++` | Jump forward by 5% of current ticks. |
| `Ctrl+D` | Increase animation ratio by `+0.5x`. |
| `Ctrl+A` | Decrease animation ratio by `-0.5x`, down to `0.5x`. |
| `Ctrl+Q` | Quit the visualisation. |
| `Ctrl+H` | Toggle the help modal. |

## Examples

The curated examples are grouped by difficulty, plus city-inspired schematic networks:

| Command | What it shows |
|---|---|
| `uv run python examples/Basic/simple_loop.py` | Starter loop with two train assets. |
| `uv run python examples/Basic/two_line_shuttle.py` | Two intersecting shuttle services. |
| `uv run python examples/Medium/signal_gate.py` | Alternating signal gates on a branch. |
| `uv run python examples/Medium/collision_lab.py` | Collision/emergency-stop behavior with a held signal. |
| `uv run python examples/Advanced/multi_asset_control_room.py` | Multiple assets, lines, and protected junctions. |
| `uv run python examples/Advanced/interlocking_corridor.py` | Interlocking corridor with several controlled approaches. |
| `uv run python examples/cities/london.py` | Minimal London Underground-inspired schematic. |
| `uv run python examples/cities/nyc.py` | Minimal NYC Subway-inspired schematic. |

## Challenges

Challenge files live in `challenges/`.

- Students implement `solve(graph, src, dst) -> list[str]`.
- `challenges/framework.py` validates the route and visualises it.
- `challenges/envs.py` defines `easy_graph`, `medium_graph`, and `london_graph`.

Instructor smoke check:

```bash
uv run python challenges/_smoke.py
```

## Headless Use

```python
from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Headless", render_scale=1).pipeline([
    Network([
        Line("Loop", Color.RED, [(0, 0), (40, 0), (40, 40), (0, 0)]),
        Station("Origin", (0, 0)),
    ]),
    Train("A", line="Loop"),
])

system.fit().step(100)
print(system.simulator.train("A").position)
```
