# LLM queueing

`MetroGYM` exposes an optional public API for using an LLM to arbitrate a queued signal junction.

!!! warning "Optional extra"
    Install the LLM dependencies with `uv sync --extra llm` before using these classes.

## ::: metrogym.primitives.signal.llm_signal_queue_handler.SignalQueueCandidate
    options:
        heading: "SignalQueueCandidate"
        inherited_members: true

## ::: metrogym.primitives.signal.llm_signal_queue_handler.SignalQueuePlan
    options:
        heading: "SignalQueuePlan"
        inherited_members: true

## ::: metrogym.primitives.signal.llm_signal_queue_handler.BaseLLMProvider
    options:
        heading: "BaseLLMProvider"
        members:
            - select_train

## ::: metrogym.primitives.signal.llm_signal_queue_handler.BaseLLMQueueSignalAgent
    options:
        heading: "BaseLLMQueueSignalAgent"
        inherited_members: true
        members:
            - __init__
            - reset
            - act

## ::: metrogym.primitives.signal.llm_signal_queue_handler.LLMSignalQueueHandler
    options:
        heading: "LLMSignalQueueHandler"
        inherited_members: true

## ::: metrogym.primitives.signal.extras.llm_signal_queue_providers.openai.OpenAIELLProvider
    options:
        heading: "OpenAIELLProvider"
        inherited_members: true
        members:
            - __init__
            - select_train
