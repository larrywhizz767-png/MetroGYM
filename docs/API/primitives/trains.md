# Trains

These primitives attach rolling stock to an already declared network.

```python hl_lines="9"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Train Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
    ]),
    Train("A", line="Loop", solver=train.always_proceed()),
])
```

[See more train examples below](#more-train-examples)

## ::: metrogym.primitives.train.train.Train
    options:
        heading: "Train"
        inherited_members: true

## More Train Examples

### Pulse timing

```python hl_lines="9"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Pulse Train Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
    ]),
    Train("A", line="Loop", solver=train.pulse(run_ticks=3, hold_ticks=2)),
])
```

### Two trains on one line

```python hl_lines="9-10"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Two Trains Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
    ]),
    Train("A", line="Loop", solver=train.always_proceed()),
    Train("B", line="Loop", start_at=50, solver=train.avoid_collisions(min_distance=60)),
])
```
