from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

# HOMEWORK 1: Massive Network
# Your task is to build a large network with at least 5 lines, including some loops.
# Do not add any signals. Add exactly 1 dummy train so the engine validation passes.

def run():
    system = MetroSystem(name="Homework 1 - Massive Network").pipeline([
        Network([
            # Add your lines and stations here!
            # Example:
            Line("Line 2", Color.BLUE, [(300, 300), (350, 350), (650, 350), (700, 300), (700, 150), (650, 100), (350, 100), (300, 150), (300, 300)]),
            Station("Xizhimen", (300, 160)),
            Station("Jishuitan", (334, 116)),
            Station("Gulou Dajie", (422, 100)),
            Station("Andingmen", (498, 100)),
            Station("Yonghegong Lama Temple", (587, 100)),
            Station("Dongzhimen", (662, 112)),
            Station("Dongsishitiao", (700, 166)),
            Station("Chaoyangmen", (700, 235)),
            Station("Jianguomen", (700, 293)),
            Station("Beijing Railway Station", (675, 325)),
            Station("Chongwenmen", (623, 350)),
            Station("Qianmen", (562, 350)),
            Station("Hepingmen", (492, 350)),
            Station("Xuanwumen", (427, 350)),
            Station("Changchunjie", (367, 350)),
            Station("Fuxingmen", (327, 327)),
            Station("Fuchengmen", (300, 282)),
            Station("Chegongzhuang", (300, 221)),

        ]),
        # Add 1 dummy train that does nothing so that the engine allows the pipeline to build
        Train("Dummy", line="Line 2", solver=train.always_hold()),
    ])

    system.fit().run()

if __name__ == "__main__":
    run()