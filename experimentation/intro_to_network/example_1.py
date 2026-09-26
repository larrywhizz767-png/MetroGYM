from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

system = MetroSystem(name="Solver Basic: Always Run", tick_ms=400, render_scale=2).pipeline([
    Network([
        Line("Loop", Color.BLUE, [(120, 120), (560, 120), (560, 360), (120, 360), (120, 120)]),
        Station("Origin", (120, 120)),
        Station("North", (560, 120)),
        Station("South", (560, 360)),
        Station("West", (120, 360)),
    ]),
        Train("A", line="Loop", solver=train.proceed(), asset="metro_nose"),
        Train("B", line="Loop", start_at=50, solver=train.proceed(), asset="city_tram")

])

system.fit().run()
