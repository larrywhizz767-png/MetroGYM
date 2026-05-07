# World views and decisions

`MetroGYM` agents inspect immutable snapshots and return typed decisions.

## Decisions

## ::: metrogym.solvers.TrainVerb
    options:
        heading: "TrainVerb"

## ::: metrogym.solvers.SignalVerb
    options:
        heading: "SignalVerb"

## ::: metrogym.solvers.TrainDecision
    options:
        heading: "TrainDecision"
        inherited_members: true

## ::: metrogym.solvers.SignalDecision
    options:
        heading: "SignalDecision"
        inherited_members: true

## World snapshots

## ::: metrogym.solvers.TrainSnapshot
    options:
        heading: "TrainSnapshot"
        inherited_members: true

## ::: metrogym.solvers.SignalSnapshot
    options:
        heading: "SignalSnapshot"
        inherited_members: true

## ::: metrogym.solvers.SignalRuleSnapshot
    options:
        heading: "SignalRuleSnapshot"
        inherited_members: true

## ::: metrogym.solvers.WorldView
    options:
        heading: "WorldView"
        inherited_members: true
        members:
            - observe_train
            - observe_signal

## ::: metrogym.solvers.TrainObservation
    options:
        heading: "TrainObservation"
        inherited_members: true

## ::: metrogym.solvers.TrainSignalView
    options:
        heading: "TrainSignalView"
        inherited_members: true

## ::: metrogym.solvers.SignalObservation
    options:
        heading: "SignalObservation"
        inherited_members: true

## ::: metrogym.solvers.SignalQueueView
    options:
        heading: "SignalQueueView"
        inherited_members: true
        members:
            - ordered
            - distance_for

## ::: metrogym.solvers.distance_to_rule
    options:
        heading: "distance_to_rule"
