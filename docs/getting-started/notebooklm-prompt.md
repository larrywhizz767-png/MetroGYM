---
icon: lucide/mic
---

# NotebookLM Prompt

Use the following prompt inside `NotebookLM` to generate a lively two-person audio overview of `MetroGYM`.

````md
You are creating a curious, exciting, intelligent podcast-style conversation between two members:

- **Maya**: the curious host who keeps asking sharp, practical questions.
- **Leo**: the technical host who explains clearly, with energy, intuition, and mathematical structure.

Your job is to explain `MetroGYM` as if the audience includes urban-computing researchers, transport-modelling labs, and urban-planning teams who need a modular underground / metro simulation library.

## Tone and delivery

- Make it sound like an engaging podcast, not a dry lecture.
- Keep both speakers active: Maya asks, challenges, reframes; Leo answers, connects ideas, and builds momentum.
- Be precise, but never boring.
- Use a sense of discovery: the audience should feel that a missing research tool is finally taking shape.
- Make the style polished, warm, and intellectually exciting.
- Do not invent capabilities that are not supported by the source material.
- If a point is uncertain, present it carefully as a direction or ambition, not as an already finished feature.

## Goal

Explain, in order:

1. **The problem**: there is still no widely adopted, lightweight, Python-native, modular library dedicated to underground / metro systems that urban-computing labs or planning teams can easily adapt, inspect, and extend.
2. **How `MetroGYM` responds to that gap**, including a mathematical framing of the metro world.
3. **What a network is**, and what lines and stations mean inside it.
4. **What a train is** in the library.
5. **What a signal is** in the library.
6. **How all these parts work together in a `scikit-learn`-inspired pipeline**.
7. **What a data-driven solver is**, and how it makes the world come alive at runtime.
8. **What comes next**: a more `GYM`-like reinforcement-learning layer for trains and signals.
9. **A strong conclusion** about why this matters for research and practice.

## Required conceptual framing

You must introduce the world with the notation:

\[
W = (N, T, G, \Pi)
\]

where:

- \(N\) is the metro **network**,
- \(T\) is the set of **trains**,
- \(G\) is the set of **signals**,
- \(\Pi\) is the collection of **policies / solvers** acting on trains and signals.

Then explain the simulation dynamics with:

\[
W_{t+1} = F(W_t, \Pi)
\]

Interpret this clearly in plain English: the next world state depends on the current declared world plus the decisions made by the train-side and signal-side solvers.

When explaining the network, make the notation slightly more concrete. For example, describe the network as containing lines and stations, such as:

\[
N = (L, S)
\]

where:

- \(L\) is the set of metro lines,
- \(S\) is the set of stations.

Then explain each part intuitively:

- a **line** is a named coloured path built from ordered waypoints in 2D space,
- a **station** is a named location placed on or near that infrastructure,
- a **train** is a moving runtime object attached to a specific line,
- a **signal** is a control object that protects a segment or access point and regulates entry.

## Mandatory content points

### 1) The problem and the motivation

Make clear that many tools exist around transport, traffic, or games, but there is a specific gap for a **clean, inspectable, programmable metro-systems library** that is:

- Python-native,
- modular,
- readable,
- explicit in its primitives,
- suitable for experimentation,
- useful for comparing alternative control strategies.

Emphasise that teams in urban computing and planning often need a world they can **declare, validate, run, and study**, rather than a black-box simulator or a giant transport platform.

### 2) How `MetroGYM` is shaped around that problem

Explain that `MetroGYM` is designed as a world-building and policy-testing library.
Describe it as a typed, modular environment where infrastructure and control logic are separated so researchers can change one without rewriting the other.

### 3) What a network is

Explain that the network is the infrastructure container. It groups:

- **Lines**: named route geometries,
- **Stations**: named stop locations.

Make clear that `Network(...)` is the required infrastructure block in the pipeline.

### 4) What a train is

Explain that a train is not just a drawing. It is an entity with:

- a line assignment,
- a position on that line,
- runtime motion,
- local observations,
- decisions driven by a solver.

Mention that trains can react to signals, spacing, and nearby traffic.

### 5) What a signal is

Explain that a signal protects movement through critical track segments.
Mention `ControlRule` as the way controlled segments are declared.
Explain that a signal solver can grant, deny, lock, pulse, or queue access depending on the current state.

### 6) The `scikit-learn`-like pipeline

You must explain the workflow in this sequence:

1. declare primitives,
2. place them into `MetroSystem(...).pipeline([...])`,
3. call `fit()` to validate and materialise runtime objects,
4. call `run()` or `step(n)` to execute the world.

Make the analogy explicit: as in `scikit-learn`, there is a separation between **declaration**, **fitting/building**, and **execution**.

### 7) What a data-driven solver is

Explain that the world becomes alive because trains and signals do not only exist geometrically; they observe world state and emit typed decisions.

State that a solver can be:

- a simple built-in policy,
- a custom rule-based agent,
- an algorithmic controller,
- optionally, in advanced cases, an LLM-backed queue planner for signal decisions.

Clarify that the solver is the operational intelligence layer of the system.

### 8) What comes next

Present the next step as an ambition: a stronger `GYM`-like reinforcement-learning layer where trains and signals could become trainable RL agents while keeping the same explicit metro-world model.

Do not claim that the RL layer is already complete. Present it as the logical future direction.

## Structure requirements

Organise the episode into short titled segments, but keep the output as a dialogue.
Suggested flow:

1. **Opening hook**
2. **Why this problem exists**
3. **The world notation: \(W = (N, T, G, \Pi)\)**
4. **Inside the network: lines and stations**
5. **Trains as moving decision-bearing objects**
6. **Signals as traffic intelligence**
7. **The pipeline: declare, fit, run**
8. **Data-driven solvers and live control**
9. **What is next for `MetroGYM`**
10. **Conclusion**

## Style constraints

- Keep the mathematics readable and spoken naturally.
- Alternate between intuition and precision.
- Use short examples in words, not code blocks.
- Avoid marketing clichés.
- Avoid generic AI buzzwords.
- Make the audience feel that `MetroGYM` sits at the intersection of software design, mathematical modelling, and urban systems research.
- End with a memorable closing reflection about why a modular metro simulation library matters.

## Final instruction

Write the final output as a polished podcast script with speaker labels:

- **Maya:**
- **Leo:**

The result should feel ready to read aloud in NotebookLM audio mode.
````
