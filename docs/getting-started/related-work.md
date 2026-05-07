---
icon: lucide/git-compare-arrows
---

# Related Work

`MetroGYM` sits near several strong open-source initiatives, but it is not trying to be the same thing as any one of them. Broadly speaking, these projects help clarify where `MetroGYM` is today and where it could go next.

## Projects worth knowing

### `OpenTTD`

[`OpenTTD`](https://github.com/OpenTTD/OpenTTD) is a large transport-management simulation game. It is excellent for network growth, routing, economics, and long-horizon transport operations.

`MetroGYM` differs in three broad ways. (i) It is a Python library rather than a full game. (ii) It focuses on explicit, programmable metro worlds instead of a player-managed transport economy. (iii) It is designed so that trains, signals, and policies can be studied directly as code-level objects.

### `CARLA`

[`CARLA`](https://github.com/carla-simulator/carla) is a major simulator for autonomous-driving research. It is particularly strong for sensor-rich environments, embodied agents, and reinforcement-learning workflows.

`MetroGYM` differs in three broad ways. (i) It focuses on metro operations rather than road-driving autonomy. (ii) It works through a much lighter declarative pipeline of primitives. (iii) It aims at rail-style control questions such as dispatch, spacing, signalling, and queue arbitration.

### `SUMO`

[`SUMO`](https://github.com/eclipse-sumo/sumo) is one of the main open-source transport simulators. It is strong for large-scale traffic simulation, demand modelling, and network-level transport studies.

`MetroGYM` differs in three broad ways. (i) It is narrower in scope and more opinionated around metro systems. (ii) It emphasises readable public primitives and typed solver interfaces rather than broad transport configuration. (iii) It aims to make policy experimentation feel closer to a machine-learning or scientific-programming workflow.

### `Mesa`

[`Mesa`](https://github.com/projectmesa/mesa) is a well-known Python framework for agent-based modelling. It is useful when building general multi-agent simulations from first principles.

`MetroGYM` differs in three broad ways. (i) It is domain-specific rather than general-purpose. (ii) It already provides metro-native objects such as lines, stations, trains, signals, and control rules. (iii) It treats the world as an operational metro environment rather than only an abstract agent-based model.

### `CityFlow`

[`CityFlow`](https://github.com/cityflow-project/CityFlow) is a fast traffic simulator built for multi-agent reinforcement-learning research, especially signal control.

`MetroGYM` differs in three broad ways. (i) It targets metro and railway-style systems rather than road traffic. (ii) It models train and signal interaction through explicit rail-world primitives. (iii) It is currently aimed at declarative world-building and solver experimentation, with a possible stronger reinforcement-learning layer still ahead.

## Where `MetroGYM` stands

Right now, `MetroGYM` is we believe understood as a flexible and modular metro-world library. Its main strengths are: (i) explicit world declaration through public primitives; (ii) a `Scikit-Learn`-like pipeline, fit, and run workflow; (iii) typed train and signal solvers that make policy logic easy to inspect, replace, and compare.

Later, we hope to be able to ship a reinforcement-learning layer on top of the current metro-world model. In that direction, trains and signals would remain explicit metro objects, but their policies could increasingly be trained rather than only hand-written.

Cheers!