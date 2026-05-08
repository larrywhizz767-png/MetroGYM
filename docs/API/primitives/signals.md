# Signals

These primitives attach junction control to a declared network and can optionally use LLM-backed queue arbitration.

```python hl_lines="9"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

system = MetroSystem(name="Signal Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
    ]),
    Signal("S1", (420, 120), controls=ControlRule("Loop", (420, 120), (420, 320))),
    Train("A", line="Loop", solver=train.respect_signals()),
])
```

[See more signal examples below](#more-signal-examples)

## Signals

## ::: metrogym.primitives.signal.signal.Signal
    options:
        heading: "Signal"
        inherited_members: true

## ::: metrogym.primitives.signal.extras.control_rule.ControlRule
    options:
        heading: "ControlRule"
        inherited_members: true

## LLM queueing

`MetroGYM` exposes an optional public API for using an LLM to arbitrate a queued signal junction.

!!! warning "Optional extra"
    Install the LLM dependencies with `uv sync --extra llm` before using these classes.

## ::: metrogym.primitives.signal.llm_signal_queue_handler.LLMSignalQueueHandler
    options:
        heading: "LLMSignalQueueHandler"
        inherited_members: true

### Providers

## ::: metrogym.primitives.signal.extras.llm_signal_queue_providers.openai.OpenAIELLProvider
    options:
        heading: "OpenAIELLProvider"
        inherited_members: true
        members:
            - __init__
            - select_train

## More Signal Examples

### Protected segment

```python hl_lines="9"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

system = MetroSystem(name="Protected Segment Demo").pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
        Station("Origin", (120, 120)),
    ]),
    Signal("S1", (420, 120), controls=ControlRule("Loop", (420, 120), (420, 320))),
    Train("A", line="Loop", solver=train.respect_signals()),
])
```

### LLM queueing signal

```python hl_lines="11"
from metrogym import Color, MetroSystem, train
from metrogym.primitives import ControlRule, LLMSignalQueueHandler, Line, Network, Station, Train

system = MetroSystem(name="LLM Queue Demo").pipeline([
    Network([
        Line("Northbound", Color.BLUE, [(120, 120), (260, 120), (360, 220)]),
        Line("Southbound", Color.RED, [(120, 320), (260, 320), (360, 220)]),
        Station("North", (120, 120)),
        Station("South", (120, 320)),
    ]),
    LLMSignalQueueHandler("J1", (360, 220), controls=[
        ControlRule("Northbound", (260, 120), (360, 220)),
        ControlRule("Southbound", (260, 320), (360, 220)),
    ], model="gpt-4o-mini"),
    Train("N1", line="Northbound", solver=train.always_proceed()),
    Train("S1", line="Southbound", solver=train.always_proceed()),
])
```
