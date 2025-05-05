from abc import ABC, abstractmethod


class Organism(ABC):

    @abstractmethod
    def get_energy(self) -> int:
        pass
    
    @abstractmethod
    def get_nutrition(self) -> int:
        pass

    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        pass



class Animal(Organism):
    def __init__(self, **kwargs) -> None:
        self.energy: int = kwargs['energy']
        self.nutrition: int = kwargs['nutrition']
        self.position: tuple[int,int] = kwargs['position']
        self.speed: int = kwargs['speed']
        self.reproduction_rate: float = kwargs['reproduction_rate']
        self.reproduction_threshold: float = kwargs['reproduction_threshold']
        self.fov: int = kwargs['fov']

    

    def get_energy(self):
        return self.energy
    
    def get_nutrition(self):
        return self.nutrition
    
    def get_position(self):
        return self.position
    

    def move(self, direction: tuple[int, int]) -> None:
        pass

    def reproduce(self, energy: int) -> None:
        pass

    def consume(self, food: Organism) -> None:
        pass

    def flee_chance(self) -> None:
        pass



class Plant(Organism):

    def __init__(self, **kwargs) -> None:
        self.energy: int = kwargs['energy']
        self.nutrition: int = kwargs['nutrition']
        self.position: tuple[int, int] = kwargs['position']
        self.grow_rate: float = kwargs['grow_rate']
    
    def get_energy(self):
        return self.energy
    
    def get_nutrition(self):
        return self.nutrition
    
    def get_position(self):
        return self.position
    
    def grow(growRate: float) -> None:
        pass


class Stage2(Animal):

    def __str__(self):
        return '2'

class Stage3(Animal):
    
    def __str__(self):
        return '3'

class Stage4(Animal):
    
    def __str__(self):
        return '4'

class Stage5(Animal):
    
    def __str__(self):
        return '5'