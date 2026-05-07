---
icon: lucide/train-front-tunnel
---

# Controlling Trains

Using the notation from [Get started](../getting-started/index.md), this tutorial focuses on the train and policy parts of the metro-world model: \(T\) and \(\Pi\). The infrastructure \(N\) is assumed to exist already. The question here is how trains observe the current world and how train-side policies turn those observations into actions.

The simplest solver examples appear in `examples/tutorials/solvers/Basic/always_run.py` and `examples/tutorials/solvers/Basic/red_signal_stop.py`. The first shows the smallest moving train through `train.always_proceed()`, whereas the second adds awareness of an upcoming signal. The medium examples then introduce periodic motion and same-line spacing constraints. The advanced examples move to target speeds, braking zones, and incident-aware control.

## Observation Model

A `TrainObservation` describes the local situation of one train at one decision point. `observation.self` contains the focused train snapshot, `observation.signals.next` reports the next relevant rule on the same line, `observation.nearby_trains` lists neighbouring trains ordered by proximity, and the collision and emergency fields expose incident state. In the world notation, this is the information used by a train-side policy inside \(\Pi\) to update the behaviour of one element of \(T\).

## Custom Train Agent

A custom train agent therefore defines part of \(\Pi\). In the example below, the policy first checks whether the next protected rule is red, then inspects spacing to the nearest neighbouring train, and finally accelerates only when the local situation is clear.

```python
from metrogym import TrainAgent, TrainObservation, train

class SafeCruise(TrainAgent):
    def act(self, observation: TrainObservation):
        next_rule = observation.signals.next
        if next_rule and not next_rule.signal_green:
            return train.hold(reason="red signal ahead")
        if observation.nearby_trains and observation.nearby_trains[0].position.distance(observation.self.position) < 70:
            return train.slow_down(0.5, reason="closing gap")
        return train.accelerate_to(2.5, reason="clear track")
```

The decision helpers form a practical vocabulary. `train.hold()` keeps the train stationary. `train.proceed()` and `train.proceed_at(speed)` continue motion at a default or target speed. `train.accelerate_to(speed)` and `train.brake_to(speed)` adjust speed towards a target value. `train.change_speed_by(delta)` modifies the target speed by a fixed amount, and `train.reverse()` moves the train in the opposite direction along the path.

Policy composition is also available. For example, `train.all_of(...)` combines several independent constraints into one solver, such as signal-respecting logic and collision-avoidance logic.

[See further in the API](../API/solvers/train-solvers.md){ .md-button }

```python
solver = train.all_of(
    train.respect_signals(approach_distance=55.0),
    train.avoid_collisions(min_distance=70.0),
)
```

## Where Next

If you want to understand how these train-side policies interact with \(G\), that is, protected segments and queue-based access control, continue with [Managing signals](managing-signals.md). If you would prefer to inspect the public solver surface directly, consult [Train solvers](../API/solvers/train-solvers.md).
