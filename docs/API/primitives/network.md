# Network

These primitives define the physical metro world before any trains or control logic are attached.

```python hl_lines="5-9"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Network Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 300), (120, 300), (120, 120)]),
        Station("Central", (120, 120)),
        Station("East", (420, 120)),
    ]),
    Train("A", line="Loop", solver=train.always_hold()),
])
```

[See more network examples below](#more-network-examples)

## ::: metrogym.primitives.network.Network
    options:
        heading: "Network"
        inherited_members: true

## ::: metrogym.primitives.line.line.Line
    options:
        heading: "Line"
        inherited_members: true

## ::: metrogym.primitives.station.station.Station
    options:
        heading: "Station"
        inherited_members: true

## ::: metrogym.primitives.line.extras.path.build_path
    options:
        heading: "build_path"

## More Network Examples

### Two lines in one world

```python hl_lines="5-11"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Two Line Demo").pipeline([
    Network([
        Line("Blue", Color.BLUE, [(120, 120), (420, 120), (420, 260)]),
        Line("Green", Color.GREEN, [(120, 320), (320, 320), (420, 260)]),
        Station("West", (120, 120)),
        Station("South", (120, 320)),
        Station("Junction", (420, 260)),
    ]),
    Train("B1", line="Blue", solver=train.always_hold()),
    Train("G1", line="Green", solver=train.always_hold()),
])
```

### Larger network layout

```python hl_lines="5-17"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Large Network Demo").pipeline([
    Network([
        Line("Red", Color.RED, [(80, 120), (240, 120), (360, 200), (520, 200)]),
        Line("Blue", Color.BLUE, [(80, 340), (240, 340), (360, 260), (520, 260)]),
        Line("Green", Color.GREEN, [(240, 40), (240, 120), (240, 340), (240, 420)]),
        Station("North", (240, 40)),
        Station("West Red", (80, 120)),
        Station("Central", (240, 120)),
        Station("Mid Exchange", (360, 200)),
        Station("West Blue", (80, 340)),
        Station("South Exchange", (240, 340)),
        Station("Harbour", (520, 260)),
        Station("South", (240, 420)),
    ]),
    Train("R1", line="Red", solver=train.always_hold()),
    Train("B1", line="Blue", solver=train.always_hold()),
    Train("G1", line="Green", solver=train.always_hold()),
])
```
