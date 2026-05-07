---
icon: lucide/waypoints
---

# Building Worlds

The notation from [Get started](../getting-started/index.md) is useful here as well. In this tutorial, the main focus is on how to declare \(N\), the network part of the metro-world model \(W = (N, T, G, \Pi)\). More precisely, this page shows how lines and stations are grouped inside one `Network(...)`, and how that infrastructure is then placed inside the outer `MetroSystem(...).pipeline([...])` declaration.

## Mental Model

The pipeline can be read in three steps. First, a `MetroSystem` gathers the declared primitives. Second, `fit()` validates that declaration and builds the runtime objects. Third, `run()` or `step(n)` executes the fitted world.

```text
MetroSystem(...)
  -> pipeline([
       Network([... lines and stations ...]),
       Train(...),
       Signal(...),
       MetroGYMRenderer(...),
     ])
  -> fit()
  -> run() / step(n)
```

The introductory examples under `examples/tutorials/networks/Basic/simple_loop.py` and `examples/tutorials/networks/Basic/two_line_shuttle.py` are the best place to begin. The first shows the basic `Network([...])` shape with one line and several stations. The second shows how multiple lines can coexist in the same world and why line names matter for train routing. After that, the medium examples such as `examples/tutorials/networks/Medium/signal_gate.py` and `examples/tutorials/networks/Medium/collision_lab.py` introduce protected segments and more deliberate layouts. The advanced examples then move to denser operational scenes.

## Minimal World Pattern

The following example shows a basic world declaration. In the notation above, this snippet mainly defines \(N\), then adds one train to begin defining \(T\). It contains one network, one line, several stations, and one train held in place before movement logic is added.

```python
from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="World Pattern").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
        Station("East", (420, 120)),
        Station("South", (420, 320)),
    ]),
    Train("A", line="Loop", solver=train.always_hold()),
])
```

!!! warning "Validation happens at fit time"
    A world must contain exactly one `Network`, at least one line, at least one station, and at least one train.


## Where Next

If you now want to define \(\Pi\) more actively so that trains move rather than merely exist, continue with [Controlling trains](controlling-trains.md). If the main interest lies in adding \(G\), that is, protected segments and junction access control, continue with [Managing signals](managing-signals.md).
