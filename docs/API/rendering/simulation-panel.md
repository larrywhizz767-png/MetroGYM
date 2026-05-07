# Simulation panel

The simulation panel stores track lines, stations, runtime objects, and camera state for the visible world.

## ::: metrogym.rendering.panel.TrackLine
    options:
        heading: "TrackLine"
        inherited_members: true

## ::: metrogym.rendering.panel.SimulationPanel
    options:
        heading: "SimulationPanel"
        inherited_members: true
        members:
            - __init__
            - add_track_line
            - addTrackLine
            - add_object
            - remove_object
            - addObject
            - add_station
            - addStation
            - tick
            - reset
            - draw
            - pan
            - zoom
