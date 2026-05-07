---
icon: lucide/circle-help
---

# FAQ

??? question "Why does `MetroGYM` use a pipeline instead of one large class?"
    `MetroGYM` keeps world construction explicit. Infrastructure, rolling stock, control logic, and rendering are declared as separate primitives in a pipeline, then validated together during `fit()`. This makes the built world easier to inspect, extend, and compare than a single large object that mixes every concern.

??? question "What are the differences between `Line`, `Station`, and `Signal`?"
    A `Line` defines the path that trains follow through the world. A `Station` marks named stopping points on that network. A `Signal` controls train movement at a point on the line, typically by granting or denying access to a protected segment. In short: lines define movement geometry, stations define passenger-facing places, and signals define traffic control.

??? question "What's a `Network`?"
    A `Network` is the infrastructure container in `MetroGYM`. It groups the `Line` and `Station` primitives that define the physical metro world. `MetroGYM` expects infrastructure to be declared inside `Network(...)`, so the library can validate the world structure clearly during `fit()`.

??? question "What's a Solver?"
    A solver is the policy object that decides what a train or signal should do at runtime. Train solvers inspect world state and return train actions such as hold, proceed, or adjust speed. Signal solvers inspect queue and traffic state and return decisions such as grant or deny. In practice, a solver is the part of the system that turns observations into actions.

??? question "How is it inspired by GYM?"
    `MetroGYM` is inspired by the idea of structured environments in reinforcement learning. The world exposes observations, accepts actions through train and signal policies, and can be stepped forward repeatedly. The long-term direction is to make `MetroGYM` a practical environment for reinforcement-learning-style agents operating over explicit metro worlds rather than only hand-written control logic.

??? question "What is `LLMSignalQueueHandler`?"
    `LLMSignalQueueHandler` is an optional public primitive for queue-based signal control. It uses an LLM-backed signal agent to choose which approaching train should be granted through a protected signal queue. The base package does not require it; it is only needed when you want that LLM-driven queueing behaviour.
