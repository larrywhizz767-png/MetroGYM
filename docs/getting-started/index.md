---
icon: lucide/play
---

# Get started

`MetroGYM` can be read as a discrete metro-world model. Let \(W = (N, T, G, \Pi)\), where \(N\) is the declared `network`,
\(T\) is the set of `trains`, \(G\) is the set of `signals`, and \(\Pi\) is the _collection_ of _train_ and _signal_ `policies` (also known as data-driven solvers)
attached to that infrastructure. The simulation then evolves through a transition rule of the form:

$$
W_{t+1} = F(W_t, \Pi)
$$

where the next world state depends on the current infrastructure, runtime state, and policy decisions. In another word,
`MetroGYM` is a highly-typed library for urban-computing researchers, and planners who want to
build explicit underground metro network simulations and study how control logic changes system behaviour.

Moreover, `MetroGYM` is inspired by the `Scikit-Learn` way of structuring workflows (i.e., `Pipeline`). To remain scalable, easy to use, shareable, and easy to extend, `MetroGYM` separates world specification, fitting, and execution into distinct phases via a main `Pipeline` workflow.
That is, first, declare a world through `MetroSystem(...).pipeline([...])`. Second, call `fit()` to validate that specification and materialise the runtime objects.
Third, execute the fitted system with `run()` or `step(n)`.

!!! tip "Policy direction"
    Right now, `MetroGYM` policies are primarily data-driven, software-engineering, and algorithmic components written explicitly in code.
    A natural next step is to make that same metro-world model more `GYM`-like, so that train and signal policies can increasingly be trained as reinforcement-learning agents rather than only hand-written.

The point is not only to draw a metro network, but to define a controlled environment in which infrastructure, operating rules, and solver policies can be changed independently and then compared under the same dynamics.

Such a modular library is useful in several scenarios. For example:

- **Real-world train-control design**: define different train and signal policies, then study how those strategies affect throughput, congestion, and safety.
- **Controlled policy comparison**: keep the same world fixed whilst testing alternative train and signal strategies under identical runtime conditions.

## Installation

Choose one of the options below.

!!! info "Python support"
    `MetroGYM` targets Python `3.10` to `3.13`.

=== "UV <span class='tab-badge tab-badge--accent'>Recommended</span>"

    ```bash
    uv add metrogym
    uv sync
    ```

    !!! tip "Need UV first?"
        See the [UV installation instructions](https://docs.astral.sh/uv/).

    If you also want the optional LLM-backed queueing components:

    ```bash
    uv add "metrogym[llm]"
    uv sync
    ```

=== "Pip <span class='tab-badge'>Standard</span>"

    ```bash
    pip install metrogym
    ```

    Optional queueing extras can be installed as follows:

    ```bash
    pip install "metrogym[llm]"
    ```

=== "Conda <span class='tab-badge'>CondaForge</span>"

    To install `MetroGYM` using `Conda`, follow these steps:

    1. Open your terminal or Anaconda Prompt.
    2. Create a new Conda environment with Python 3.10:

    ```bash
    conda create --name metrogym -c conda-forge python=3.10
    ```

    3. Activate the environment:

    ```bash
    conda activate metrogym
    ```

    4. Install `MetroGYM`:

    ```bash
    pip install metrogym
    ```

=== "Jupyter with UV <span class='tab-badge'>1 line</span>"

    Launch `Jupyter Lab` with `MetroGYM` in a temporary environment managed by `UV`:

    ```bash
    uv run --with metrogym jupyter lab
    ```

    This uses your default Python (`3.10` to `3.13`). To pin a specific Python, pass `--python <path_or_version>`.

=== "From source"

    ```bash
    git clone git@github.com:larrywhizz767-png/MetroGYM.git
    cd MetroGYM
    uv sync
    ```

---

!!! bug "Have trouble installing `MetroGYM`?"
Known issues and workarounds live in
the [installation and troubleshooting](../developers.md#installation-troubleshooting) section of the Developers guide.
