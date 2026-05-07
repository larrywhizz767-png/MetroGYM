---
icon: lucide/pickaxe
---

# Advanced Scenarios

Using the notation from [Get started](../getting-started/index.md), advanced scenarios are the cases in which the interaction among \(N\), \(T\), \(G\), and \(\Pi\) becomes denser and more difficult to reason about locally. The focus is no longer on one isolated part of the metro-world model, but on how the full system behaves once infrastructure, signalling, and policies interact at the same time.

The advanced network examples are one route into that material. `examples/tutorials/networks/Advanced/interlocking_corridor.py` shows a multi-line corridor with several protected junctions in the same scene. `examples/tutorials/networks/Advanced/multi_asset_control_room.py` extends that idea with several train assets and a larger operational layout. `examples/tutorials/networks/Advanced/circular_city_ring.py` then shows how circular geometry and radial connections can still be represented with the same declarative world-building pattern used in the earlier tutorials.

A second route concerns advanced solver behaviour. `examples/tutorials/solvers/Advanced/circular_ring_dispatch.py` studies dispatch on a circular topology, whilst `examples/tutorials/solvers/Advanced/collision_response.py` and `examples/tutorials/solvers/Advanced/event_reactive_control.py` examine incident handling and signal decisions reacting to queue and event state. `examples/tutorials/solvers/Advanced/four_train_junction_queue.py` is particularly useful when the goal is to study how one protected point can arbitrate among several trains.

`MetroGYM` also includes a small set of city reproduction examples. Files such as `examples/cities_reproduction/beijing.py`, `examples/cities_reproduction/london.py`, `examples/cities_reproduction/nyc.py`, and `examples/cities_reproduction/paris.py` show how the same primitive-based structure can support interchange logic, denser interlocking patterns, collision-response scenarios, and maintenance-oriented operational logic.

## Optional LLM Queueing

An optional extension is available if you want to experiment with queue planners backed by a Large Language Model (LLM). In the world notation, this means replacing part of the ordinary signal-side policy set \(\Pi\) with an LLM-backed queueing policy, rather than changing the infrastructure model itself.

```bash
uv sync --extra llm
```

After installing the extra, export `OPENAI_API_KEY`. OpenAI explains how to create and manage API keys in its [API key settings](https://platform.openai.com/api-keys). You can then use `LLMSignalQueueHandler` in the relevant signal-control setup. The example `examples/tutorials/solvers/Advanced/llm_signal_queue.py` is the clearest starting point because it shows one LLM-controlled junction with several approaching trains and ordinary train guardrails around it.

!!! warning "Be aware of cost"
    LLM calls cost money. OpenAI lists current model pricing in its [pricing documentation](https://openai.com/pricing/).
