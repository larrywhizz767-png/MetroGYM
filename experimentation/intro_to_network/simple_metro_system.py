from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainAgent, TrainObservation, TrainDecision




class TrainHold(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.hold()


class TrainProceed(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.proceed()


class TrainProceedAt2(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.proceed_at(2.0)


class TrainAccelerate(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.accelerate_to(3.0)


class TrainBrake(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.brake_to(0.5)


class ChangeSpeed(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.change_speed_by(1.0)

class MoreIntelligentSolver(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        tick = observation.world.tick
        if tick < 22:
            return train.proceed_at(observation.self.default_speed)
        elif tick < 42:
            return train.hold()
        elif tick < 62:
            return train.reverse()
        else:
            return train.proceed_at(observation.self.default_speed * 2.0)





choice = input(
    "Choose an action "
    "(reverse, hold, proceed, proceed2, accelerate, brake, change, more intelligent solver): "
).lower()

# Select the corresponding solver
if choice == "reverse":
    solver = TrainReverse()
elif choice == "proceed":
    solver = TrainProceed()
elif choice == "proceed2":
    solver = TrainProceedAt2()
elif choice == "accelerate":
    solver = TrainAccelerate()
elif choice == "brake":
    solver = TrainBrake()
elif choice == "change":
    solver = ChangeSpeed()
elif choice == "more intelligent solver":
    solver = MoreIntelligentSolver()
else:
    solver = TrainHold()

system = MetroSystem(
    name="Train Action Tester",
    tick_ms=400,
    render_scale=2
).pipeline([
    Network([
        Line(
            "Loop",
            Color.BLUE,
            [(120, 120), (560, 120), (560, 360),
             (120, 360), (120, 120)]
        ),
        Station("Origin", (120, 120)),
        Station("North", (560, 120)),
        Station("South", (560, 360)),
        Station("West", (120, 360)),
    ]),
    Train("A", line="Loop", solver=solver, asset="metro_nose"),
])

system.run()

system.save("my_system.pkl")
