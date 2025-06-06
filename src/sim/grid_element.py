from sim.organism import *
from enum import Enum
import json

class TerrainType(str, Enum):
    ROCK = "ROCK"
    WATER = "WATER"
    DIRT = "DIRT"

    def colors_dict():
        return {
            TerrainType.ROCK: "gray",
            TerrainType.WATER: "blue",
            TerrainType.DIRT: "brown"
        }

class GridElement:
    

    def __init__(self, **kwargs):
        self.organisms: list[Organism] = []
        self.position: tuple[int, int] = kwargs['position']
        self.terrain: TerrainType = kwargs['terrain']
        self.sunlight_lvl: int = 0

    def get_dict(self) -> dict:
        # initial_dict = vars(self)
        initial_dict = {
            'position_x': self.position[0],
            'position_y': self.position[1],
            'terrain': json.dumps(self.terrain).strip("\""),
            'organisms': [i.get_dict() for i in self.organisms],
            'sunlight_lvl': self.sunlight_lvl
        }
        return initial_dict

    def get_neighbors(self, fov: int) -> list[Organism]:
        """
        This method should be called from Chainy to get neighboring organisms within field of view.
        The implementation depends on the grid structure in Chainy.
        """
        return []

    def is_empty(self) -> bool:
        return len(self.organisms) == 0
    
    def kill_organism(self, organism: Organism) -> None:
        """Remove an organism from this grid element"""
        if organism in self.organisms:
            self.organisms.remove(organism)
            
    def add_organism(self, organism: Organism) -> None:
        """Add an organism to this grid element"""
        self.organisms.append(organism)
        
    def get_organisms(self) -> list[Organism]:
        """Get all organisms in this grid element"""
        return self.organisms
        
    def update_sunlight(self, level: int) -> None:
        """Update the sunlight level for this grid element"""
        self.sunlight_lvl = level
