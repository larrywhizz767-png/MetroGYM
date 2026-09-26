from metrogym import Color, MetroSystem, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

# HOMEWORK 3: Many Signals
# Your task is to add signals to protect the 4 intersections in this grid.
# The intersections are at (300, 300), (600, 300), (300, 500), and (600, 500).
# The signals should have dummy solvers like signal.pulse()
# Remember to also add trains that use solver=train.respect_signals() so you can see them wait!

def run():
    system = MetroSystem(name="Homework 3 - Many Signals").pipeline([
        Network([
            # Vertical lines
            Line("NS1", Color.RED, [(300, 100), (300, 250), (300, 350), (300, 450), (300, 550), (300, 700)]),
            Station("NS1 North", (300, 100)),
            Station("NS1 South", (300, 700)),

            Line("NS2", Color.BLUE, [(600, 100), (600, 250), (600, 350), (600, 450), (600, 550), (600, 700)]),
            Station("NS2 North", (600, 100)),
            Station("NS2 South", (600, 700)),

            # Horizontal lines
            Line("EW1", Color.GREEN, [(100, 300), (250, 300), (350, 300), (550, 300), (650, 300), (800, 300)]),
            Station("EW1 West", (100, 300)),
            Station("EW1 East", (800, 300)),

            Line("EW2", Color.YELLOW, [(100, 500), (250, 500), (350, 500), (550, 500), (650, 500), (800, 500)]),
            Station("EW2 West", (100, 500)),
            Station("EW2 East", (800, 500)),

            # Intersections
            Station("NW Hub", (300, 300)),
            Station("NE Hub", (600, 300)),
            Station("SW Hub", (300, 500)),
            Station("SE Hub", (600, 500)),
        ]),

        # Add train(s) that use solver=train.respect_signals()
        Train("NS1-T1", line="NS1", start_at=10, solver=train.respect_signals()),
        Train("NS1-T2", line="NS1", start_at=80, solver=train.respect_signals()),
        Train("NS2-T1", line="NS2", start_at=25, solver=train.respect_signals()),
        Train("NS2-T2", line="NS2", start_at=55, solver=train.respect_signals()),
        Train("EW1-T1", line="EW1", start_at=75, solver=train.respect_signals()),
        Train("EW1-T2", line="EW1", start_at=60, solver=train.respect_signals()),
        Train("EW2-T1", line="EW2", start_at=50, solver=train.respect_signals()),
        Train("EW2-T2", line="EW2", start_at=30, solver=train.respect_signals()),


        # Add signals with solver=signal.pulse() and ControlRule to protect the crossings
        # Example:
        Signal("S1", (300, 250), controls=ControlRule("NS1", (300, 250), (300, 350)), solver=signal.pulse()),
        Signal("S2", (275, 500), controls=ControlRule("EW2", (250, 500), (350, 500)), solver=signal.pulse()),
        Signal("S3", (275, 300), controls=ControlRule("EW1", (250, 300), (350, 300)), solver=signal.pulse()),
        Signal("S4", (600, 250), controls=ControlRule("NS2", (600, 250), (600, 350)), solver=signal.pulse())

    ])

    system.fit().run()

if __name__ == "__main__":
    run()
