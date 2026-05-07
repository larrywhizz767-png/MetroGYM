# Train solvers

Train agents and helper namespaces define how trains move through the world.

## Base protocol and agent

## ::: metrogym.solvers.TrainSolver
    options:
        heading: "TrainSolver"

## ::: metrogym.solvers.TrainAgent
    options:
        heading: "TrainAgent"
        inherited_members: true
        members:
            - reset
            - observe
            - act
            - __call__

## Built-in train agents

## ::: metrogym.solvers.AlwaysRunSolver
    options:
        heading: "AlwaysRunSolver"
        inherited_members: true

## ::: metrogym.solvers.AlwaysStopSolver
    options:
        heading: "AlwaysStopSolver"
        inherited_members: true

## ::: metrogym.solvers.PulseTrainSolver
    options:
        heading: "PulseTrainSolver"
        inherited_members: true

## ::: metrogym.solvers.RedSignalStopSolver
    options:
        heading: "RedSignalStopSolver"
        inherited_members: true

## ::: metrogym.solvers.CollisionAwareSolver
    options:
        heading: "CollisionAwareSolver"
        inherited_members: true

## ::: metrogym.solvers.CompositeTrainSolver
    options:
        heading: "CompositeTrainSolver"
        inherited_members: true

## ::: metrogym.solvers.AllOfTrainPolicies
    options:
        heading: "AllOfTrainPolicies"
        inherited_members: true

## ::: metrogym.solvers.AnyOfTrainPolicies
    options:
        heading: "AnyOfTrainPolicies"
        inherited_members: true

## Train helper namespace

## ::: metrogym.solvers._TrainNamespace
    options:
        heading: "train"
        members:
            - proceed
            - hold
            - reverse
            - coast
            - set_speed
            - proceed_at
            - reverse_at
            - accelerate_to
            - brake_to
            - change_speed_by
            - speed_up
            - slow_down
            - always_proceed
            - always_hold
            - pulse
            - respect_signals
            - avoid_collisions
            - all_of
            - any_of
