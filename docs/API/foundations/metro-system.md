# Metro system

`MetroSystem` is the public build-and-run facade for `MetroGYM`.

??? tip "Why start here?"
    This is the object that owns the pipeline, materialises runtime state, and exposes `fit()`, `run()`, `step()`, `reset()`, `get_params()`, and `set_params()`.

## ::: metrogym.system.MetroSystem
    options:
        heading: "MetroSystem"
        inherited_members: true
        members:
            - __init__
            - pipeline
            - fit
            - run
            - step
            - reset
            - get_params
            - set_params
