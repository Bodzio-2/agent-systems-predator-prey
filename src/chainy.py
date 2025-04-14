from organism import *
from grid_element import *

class Chainy:
    def __init__(self):
        self.organisms: list[Organism] = []
        self.grid: list[list[GridElement]] = []
        self.size: tuple[int, int] = (0,0)
        self.time_step: int = 0
        self.sim_speed: float = 1
        self.stats: list[float] = []


    
    def init_grid(self) -> None:
        pass

    def update(self) -> None:
        pass

    def spawn_plants(self) -> None:
        pass

    def generate_stats(self) -> None:
        pass

    def display(self) -> None:
        pass


