from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainAgent, TrainObservation, TrainDecision

class SimpleAgent(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        # Think about what classes are involved here during one iteration!
        return train.proceed()

def run():
    system = MetroSystem(name="Simple Hierarchy World").pipeline([
        Network([
            Line("Main", Color(0, 0, 255), [(100, 100), (500, 100)]),
            Station("A", (100, 100)),
            Station("B", (500, 100)),
        ]),
        Train("T1", line="Main", solver=SimpleAgent()),
    ])
    system.fit().run()

if __name__ == "__main__":
    run()