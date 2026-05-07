---
icon: lucide/git-commit-horizontal
---

# Managing Signals

The notation from [Get started](../getting-started/index.md) is useful here as well. In this tutorial, the main focus is on how to declare \(G\), the signal part of the metro-world model \(W = (N, T, G, \Pi)\). More precisely, this page shows how protected segments are defined and how signal-side policies inside \(\Pi\) control access to them once \(N\) and \(T\) already exist.

The introductory material begins with `examples/tutorials/networks/Medium/signal_gate.py`, which shows a basic protected segment, and with `examples/tutorials/solvers/Basic/red_signal_stop.py`, which shows how train-side logic reacts to signal state. The more advanced control examples then move to junction arbitration and queue-aware control. For LLM-backed queue planning, see [Optional LLM Queueing in Advanced Scenarios](advanced-scenarios.md#optional-llm-queueing).

## Core Pattern

The following declaration shows the essential shape of one element of \(G\). The signal is placed at a position in the world, one `ControlRule` defines the protected segment on the line, and the solver determines how the light changes over time.

```python
from metrogym import signal
from metrogym.primitives import ControlRule, Signal

Signal(
    "North Gate",
    (560, 85),
    controls=ControlRule("Loop", (560, 120), (560, 360)),
    solver=signal.pulse(green_ticks=5, red_ticks=3),
)
```

The built-in helper family covers the main introductory use cases. `signal.auto()` defers to timer behaviour already associated with the light. `signal.grant()` and `signal.deny()` provide direct binary control. `signal.lock_all()` keeps all relevant approaches red until a condition is cleared. `signal.toggle()` alternates state explicitly. `signal.pulse(...)` provides a simple phased schedule, whilst `signal.priority_queue(...)` introduces queue-aware control in which approaching trains are granted passage one at a time.

## Custom Signal Agent

A custom signal agent therefore defines part of \(\Pi\) on the signal side. In the example below, a conflict in the queue causes the controller to lock all approaches. If a next train has already been selected, that train is granted passage. Otherwise, the controller simply grants passage according to the default rule.

```python
from metrogym import SignalAgent, SignalObservation, signal

class JunctionController(SignalAgent):
    def act(self, observation: SignalObservation):
        if observation.queue.has_conflict:
            return signal.lock_all(reason="resolve queue first")
        if observation.queue.next_train is not None:
            return signal.grant(observation.queue.next_train)
        return signal.grant()
```

## Where Next

If you want to see how these control ideas behave in denser worlds, continue with [Advanced scenarios](advanced-scenarios.md). If your main interest lies in the public solver interface itself, consult [Signal solvers](../API/solvers/signal-solvers.md).
