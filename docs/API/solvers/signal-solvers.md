# Signal solvers

Signal agents decide who may enter protected track segments.

## Base protocol and agent

## ::: metrogym.solvers.SignalSolver
    options:
        heading: "SignalSolver"

## ::: metrogym.solvers.SignalAgent
    options:
        heading: "SignalAgent"
        inherited_members: true
        members:
            - reset
            - observe
            - act
            - __call__

## Built-in signal agents

## ::: metrogym.solvers.FixedSignalSolver
    options:
        heading: "FixedSignalSolver"
        inherited_members: true

## ::: metrogym.solvers.PulseSignalSolver
    options:
        heading: "PulseSignalSolver"
        inherited_members: true

## ::: metrogym.solvers.PriorityQueueSignalSolver
    options:
        heading: "PriorityQueueSignalSolver"
        inherited_members: true

## Signal helper namespace

## ::: metrogym.solvers._SignalNamespace
    options:
        heading: "signal"
        members:
            - auto
            - grant
            - deny
            - lock_all
            - toggle
            - always_grant
            - always_deny
            - pulse
            - priority_queue

## Solver utilities

## ::: metrogym.solvers.reset_solver_state
    options:
        heading: "reset_solver_state"
