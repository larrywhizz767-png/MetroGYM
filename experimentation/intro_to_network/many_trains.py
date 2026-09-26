from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

# HOMEWORK 2: Many Trains
# Your task is to add many trains (at least 6) to this network.
# Use different starting positions (start_at=...) and standard solvers
# like train.always_proceed() or train.always_hold()

def run():
    system = MetroSystem(name="Homework 2 - Many Trains").pipeline([
        Network([
            Line("Red Line", Color.RED, [(100, 300), (700, 300)]),
            Station("West", (100, 300)),
            Station("East", (700, 300)),

            Line("Blue Line", Color.BLUE, [(400, 100), (400, 500)]),
            Station("North", (400, 100)),
            Station("South", (400, 500)),
        ]),
        # Add your trains here!
        # Example:
        Train("A", line="Red Line", start_at=50, solver=train.always_proceed()),
        Train("B", line="Red Line", start_at=20, solver=train.always_hold()),
        Train("C", line="Red Line", start_at=10, solver=train.pulse()),
        Train("D", line="Blue Line", start_at=30, solver=train.always_hold()),
        Train("E", line="Blue Line", start_at=70, solver=train.always_proceed()),
        Train("F", line="Blue Line", start_at=90, solver=train.pulse())


    ])

    system.fit().run()

if __name__ == "__main__":
    run()