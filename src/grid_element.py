from organism import *
from enum import Enum

class TerrainType(Enum):
    ROCK = 1
    WATER = 2
    DIRT = 3

class GridElement:
    

    def __init__(self, **kwargs):
        self.organisms: list[Organism] = []
        self.position: tuple[int, int] = kwargs['position']
        self.terrain: TerrainType = kwargs['terrain']
        self.sunlight_lvl: int = 0

    
    def get_neighbors(self,fov: int) -> list[Organism]:
        pass

    def is_empty(self) -> bool:
        return len(self.organisms) == 0
    
    def kill_organism(species: Organism) -> None:
        pass
