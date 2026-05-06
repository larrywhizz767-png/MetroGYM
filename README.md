# MetroGYM

MetroGYM is a pure Python, pygame-powered teaching library for metro-network simulation, signalling, and control logic. It is intentionally small and inspectable: you build a network from primitives, attach train and signal agents, then run it visually or headlessly.

## Install

```bash
uv sync
```

Python requirement: `>=3.10,<3.14`.

## Quick Start

```python
from metrogym import Color, MetroSystem, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

system = MetroSystem(name="Quick Start", render_scale=2).pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (560, 120), (560, 360), (120, 360), (120, 120)]),
        Station("West", (120, 120)),
        Station("North", (560, 120)),
        Station("South", (560, 360)),
    ]),
    Train("A", line="Loop", solver=train.always_proceed(), asset="metro_nose"),
    Signal(
        "North Gate",
        (560, 85),
        controls=ControlRule("Loop", (560, 120), (560, 360)),
        solver=signal.pulse(green_ticks=5, red_ticks=3),
    ),
])

system.fit().run()
```

## Agent UX

The public solver surface now supports domain-specific observations and typed decisions.

### Train decisions

```python
from metrogym import TrainAgent, TrainObservation, train

class SafeCruise(TrainAgent):
    def act(self, observation: TrainObservation):
        if observation.signals.next and not observation.signals.next.signal_green:
            return train.hold(reason="red signal ahead")
        return train.accelerate_to(3.0, reason="clear track ahead")
```

### Signal decisions

```python
from metrogym import SignalAgent, SignalObservation, signal

class JunctionController(SignalAgent):
    def act(self, observation: SignalObservation):
        if observation.queue.has_conflict:
            return signal.lock_all(reason="resolve conflict first")
        if observation.queue.next_train is not None:
            return signal.grant(observation.queue.next_train)
        return signal.grant()
```

### Speed control actions

```python
from metrogym import train

train.accelerate_to(4.0)
train.brake_to(1.0)
train.change_speed_by(-0.5)
train.speed_up(0.5)
train.slow_down(0.5)
train.proceed_at(2.0)
```

Train speed now eases per tick toward its target rather than jumping instantly.

### Built-in combinators

```python
from metrogym import train

solver = train.all_of(
    train.respect_signals(approach_distance=55.0),
    train.avoid_collisions(min_distance=70.0),
)
```

## Core Layout

```text
src/metrogym/
  __init__.py                       public package exports
  system.py                         MetroSystem pipeline facade and validation
  context.py                        MetroContext shared build state
  runtimes.py                       RuntimeSimulator and runtime snapshots
  controls.py                       ControlSystem and segment protection
  events.py                         passive event records such as collisions
  solvers.py                        agent decisions, observations, helpers, combinators
  validation.py                     YAML-backed validation registry and structured issues
  rules/validation.yaml             declarative validation catalog

  core/
    colors.py                       Color palette and ColorRGBA
    coordinates.py                  Position and direction helpers
    constants.py                    shared simulation constants

  primitives/
    network.py                      required Network aggregator
    line/                           line primitive and runtime line
    station/                        station primitive and runtime station
    train/                          train primitive and runtime motion logic
    signal/                         signal primitive and runtime traffic light

  rendering/
    panel.py                        SimulationPanel tick and draw loop
    _utils/                         pygame helpers and keyboard shortcuts
    primitives/metrogym_renderer/   renderer primitive and runtime renderer
```

Root-level teaching material:

```text
examples/                           runnable MetroGYM scenes
challenges/                         graph-search teaching challenges
```

## Public Primitives

| Primitive | Purpose |
|---|---|
| `MetroSystem` | Owns runtime parameters, pipeline steps, validation, build, and run life cycle. |
| `Network` | Required aggregator for infrastructure primitives. |
| `Line` | Defines a named coloured path from waypoints. Must be inside `Network`. |
| `Station` | Defines a labelled station marker. Must be inside `Network`. |
| `Train` | Defines rolling stock attached to a line. `start_at=50` starts halfway along the path; same-line trains peer-check by default. |
| `Signal` | Defines a traffic signal and optional controlled segments. |
| `ControlRule` | Value object used inside `Signal(..., controls=...)`. |
| `MetroGYMRenderer` | Optional renderer primitive for renderer-level parameters such as `scale`. |

## Validation Rules

`fit()` validates the pipeline and runtime graph.

Validation is now driven by `src/metrogym/rules/validation.yaml`, with Python validators in `src/metrogym/validation.py` handling graph and geometry-aware checks.

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

## Fit / Run Life Cycle

`fit()` performs the build and validation:

1. creates the internal runtime engine from `MetroSystem` parameters;
2. applies the `Network` infrastructure primitives;
3. applies train primitives;
4. applies signal/control primitives;
5. applies renderer configuration primitives;
6. auto-peers trains on the same line unless `peer_with_line=False`;
7. stores the build context and runtime simulator on the system.

`run()` starts the pygame loop. `step(n)` advances headlessly by `n` ticks.

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

If the signal is red, trains cannot enter the controlled segment. Trains already inside the segment continue through.

## Runtime Controls

While a pygame window is open:

| Shortcut | Action |
|---|---|
| `Ctrl+R` | Restart from tick 0. |
| `Ctrl+-` | Jump backward by 5% of current ticks. |
| `Ctrl++` | Jump forward by 5% of current ticks. |
| `Ctrl+D` | Increase animation ratio by `+0.5x`. |
| `Ctrl+A` | Decrease animation ratio by `-0.5x`, down to `0.5x`. |
| `Ctrl+L` | Cycle the large transparent log overlay through `off`, `minimalist`, `trains`, `signals`, and `collisions`. Collision rows are highlighted in red. |
| Left mouse drag | Pan the map and grid. |
| Mouse wheel | Zoom in and out. |
| `Ctrl+Q` | Quit the visualisation. |
| `Ctrl+H` | Toggle the help modal. |

## Examples

Examples are split into city reproductions and tutorials. Network tutorials keep trains stopped so learners can focus on topology; solver tutorials add the control logic.

For optional LLM-backed signal queueing, install the extra with `uv sync --extra llm` and export `OPENAI_API_KEY`. Use the `LLMSignalQueueHandler` primitive to create an LLM-backed signal post, with provider-specific implementations under `primitives/signal/providers/` and OpenAI enabled by default. Pick the model with `model=...`, optionally pass a `decision_prompt`, and control exposed context with `include_signal_state`, `include_queue_candidates`, and `include_world_state`.

| Command | What it shows |
|---|---|
| `uv run python examples/cities_reproduction/london.py` | London-style multi-line schematic with interlocking, train spacing, signals, and maintenance response. |
| `uv run python examples/cities_reproduction/nyc.py` | NYC-style multi-borough schematic with dispatching, interlocking, train spacing, and maintenance service. |
| `uv run python examples/cities_reproduction/beijing.py` | Minimal Beijing-inspired network with ring, trunk, airport, and intelligent interchange signals. |
| `uv run python examples/cities_reproduction/paris.py` | Paris-style spacious network with Metro and RER solvers, acceleration/braking profiles, a deliberate Bastille collision, and maintenance inspection response. |
| `uv run python examples/tutorials/networks/Basic/simple_loop.py` | Basic network: one loop, stations, and stopped train assets. |
| `uv run python examples/tutorials/networks/Basic/two_line_shuttle.py` | Basic network: two crossing shuttle lines. |
| `uv run python examples/tutorials/networks/Medium/signal_gate.py` | Medium network: branch topology with signal primitives. |
| `uv run python examples/tutorials/networks/Medium/collision_lab.py` | Medium network: protected loop, service spur, and collision geometry. |
| `uv run python examples/tutorials/networks/Advanced/interlocking_corridor.py` | Advanced network: multiple junctions and interlocking signal posts. |
| `uv run python examples/tutorials/networks/Advanced/multi_asset_control_room.py` | Advanced network: several lines, assets, depots, and central junctions. |
| `uv run python examples/tutorials/networks/Advanced/circular_city_ring.py` | Advanced network: circular city ring with radial chords, merge signals, and orbital geometry. |
| `uv run python examples/tutorials/solvers/Basic/always_run.py` | Basic agent API: a train that always proceeds. |
| `uv run python examples/tutorials/solvers/Basic/red_signal_stop.py` | Basic agent API: a train that holds for a red signal. |
| `uv run python examples/tutorials/solvers/Medium/pulse_train.py` | Medium agent API: pulse-running train with a signal-aware peer. |
| `uv run python examples/tutorials/solvers/Medium/collision_aware.py` | Medium agent API: faster follower holds before colliding. |
| `uv run python examples/tutorials/solvers/Advanced/event_reactive_control.py` | Advanced agent API: two trains queue through a stable lock-then-grant junction. |
| `uv run python examples/tutorials/solvers/Advanced/collision_response.py` | Advanced agent API: broken signal causes collision, maintenance response, and reset. |
| `uv run python examples/tutorials/solvers/Advanced/four_train_junction_queue.py` | Advanced variant: four trains share one queued junction safely. |
| `uv run python examples/tutorials/solvers/Advanced/llm_signal_queue.py` | Advanced LLM primitive: an `LLMSignalQueueHandler` holds all trains, asks OpenAI which train to release next, then grants the chosen route. |
| `uv run python examples/tutorials/solvers/Advanced/circular_ring_dispatch.py` | Advanced circular solver: ring trains and chords coordinate through merge dispatchers. |
| `uv run python examples/tutorials/solvers/Advanced/speed_ramp_commuter.py` | Advanced speed solver: trains ramp smoothly into faster commuter cruising. |
| `uv run python examples/tutorials/solvers/Advanced/signal_brake_profile.py` | Advanced speed solver: trains brake progressively into a timed signal approach. |

## Challenges

Algorithm puzzles live in `challenges/puzzles/`. They are solved by default, print their process and result in the console, and open a MetroGYM visualisation when run directly.

| Command | Concept |
|---|---|
| `uv run python challenges/puzzles/01_bfs_shortest_stops.py` | Breadth-first search on an unweighted metro graph. |
| `uv run python challenges/puzzles/02_binary_search_arrivals.py` | Binary search for the first arrival at or after a target tick. |
| `uv run python challenges/puzzles/03_dijkstra_fastest_route.py` | Weighted fastest-route search. |
| `uv run python challenges/puzzles/04_dispatch_queue.py` | Greedy dispatch ordering for a merge segment. |
| `uv run python challenges/puzzles/05_signal_interlocking.py` | Safe release order for conflicting signal paths. |

Headless puzzle smoke check:

```bash
uv run python challenges/puzzles/_smoke.py
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
