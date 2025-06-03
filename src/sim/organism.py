from abc import ABC, abstractmethod
from enum import Enum
import json
import random

class OrganismType(str, Enum):
    PLANT = "PLANT"
    STAGE2 = "STAGE2"
    STAGE3 = "STAGE3"
    STAGE4 = "STAGE4"
    STAGE5 = "STAGE5"

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

    @abstractmethod
    def get_organism_type(self) -> OrganismType:
        pass

    def get_dict(self) -> dict:
        # initial_dict = vars(self)
        initial_dict = {
            'energy': int(self.get_energy()),
            # 'nutrition': self.get_nutrition(),
            # 'position': self.get_position(),
            # 'speed': self.speed if hasattr(self, 'speed') else 0,
            # 'reproduction_rate': self.reproduction_rate if hasattr(self, 'reproduction_rate') else 0,
            # 'reproduction_threshold': self.reproduction_threshold if hasattr(self, 'reproduction_threshold') else 0,
            # 'fov': self.fov if hasattr(self, 'fov') else 0,
            # 'grow_rate': self.grow_rate if hasattr(self, 'grow_rate') else 0
        }
        initial_dict['organism_type'] = json.dumps(self.get_organism_type()).strip('\"')
        return initial_dict



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
    
    def get_organism_type(self):
        if isinstance(self, Stage2):
            return OrganismType.STAGE2
        elif isinstance(self, Stage3):
            return OrganismType.STAGE3
        elif isinstance(self, Stage4):
            return OrganismType.STAGE4
        else:
            return OrganismType.STAGE5


    def move(self, direction: tuple[int, int]) -> None:
        """
        Move the animal in the specified direction
        direction: (dx, dy) tuple indicating the direction to move
        """
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)
        self.position = (x + dx, y + dy)
        self.energy -= (abs(dx) + abs(dy)) * (0.5 if self.stage == 2 else 0.15)

    def reproduce(self) -> 'Animal':
        """
        Create a new animal of the same type if reproduction conditions are met
        Returns a new animal or None if reproduction isn't possible
        """
        if self.energy > self.reproduction_threshold:

            offspring_energy = self.energy // 2
            self.energy -= offspring_energy
            

            return self.__class__(
                energy=offspring_energy,
                nutrition=self.nutrition,
                position=self.position, 
                speed=self.speed,
                reproduction_rate=self.reproduction_rate,
                reproduction_threshold=self.reproduction_threshold,
                fov=self.fov
            )
        return None

    def eat(self, food: Organism, sim=None) -> None:
        """
        Eat a food organism, applying the 10% energy rule if it's an animal,
        or standard gain if it's a plant.
        """
        if isinstance(food, Plant):
            gained_energy = food.get_nutrition()
            if isinstance(self, Stage2):
                gained_energy *= 1.5
            self.energy += gained_energy
        elif isinstance(food, Animal):
            gained_energy = int(food.energy * 0.1)
            self.energy += gained_energy
        else:
            # Fallback: just use nutrition
            self.energy += food.get_nutrition()
        
        # Remove the eaten organism from the simulation if sim is provided
        if sim:
            sim.remove_organism(food)


    def flee_chance(self, predator: 'Animal') -> bool:
        """
        Determine if this animal can flee from a predator
        predator: the animal trying to consume this one
        Returns: True if the animal successfully flees, False otherwise
        """
        if self.speed > predator.speed:
            return True
        elif self.speed == predator.speed:
            import random
            return random.random() > 0.5
        else:
            import random
            ratio = self.speed / predator.speed
            return random.random() < ratio


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
    
    def get_organism_type(self):
        return OrganismType.PLANT

    def grow(self, sunlight: int = 0) -> None:
        """Increase the plant's energy and nutrition based on sunlight and grow rate"""
        growth = max(1, int(sunlight * self.grow_rate * 0.2))  # Buffed growth
        self.energy += growth
        self.nutrition += growth // 2

        # Optional plant reproduction (spreading)
        if self.energy > 60 and random.random() < 0.05:  # 5% chance to reproduce
            # Generate nearby coordinates (8 surrounding tiles)
            nearby = [(self.position[0] + dx, self.position[1] + dy)
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)]

            random.shuffle(nearby)  # Randomize to avoid directional bias

            for nx, ny in nearby:
                # Ensure the location is in-bounds and empty
                if 0 <= nx < sim.size[0] and 0 <= ny < sim.size[1]:
                    if sim.get_organism_at((nx, ny)) is None:
                        sim.add_organism("plant", (nx, ny),
                                        energy=10,
                                        nutrition=5,
                                        grow_rate=self.grow_rate * 0.9)  # slightly lower grow rate
                        self.energy -= 10  # Energy cost to spawn a new plant
                        break  # Reproduce only once per grow cycle



class Stage2(Animal):
    """Primary Herbivore - eats plants only"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    def can_eat(self, organism: Organism) -> bool:
        """Stage2 animals can only eat plants"""
        return isinstance(organism, Plant)
    
    def __str__(self):
        return "2"


class Stage3(Animal):
    """Omnivore - eats plants and Stage2 animals"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    def can_eat(self, organism: Organism) -> bool:
        """Stage3 animals can eat plants and Stage2 animals"""
        return isinstance(organism, Plant) or isinstance(organism, Stage2)
    
    def __str__(self):
        return "3"


class Stage4(Animal):
    """Primary Carnivore - eats Stage2 and Stage3 animals"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    def can_eat(self, organism: Organism) -> bool:
        """Stage4 animals can eat Stage2 and Stage3 animals"""
        return isinstance(organism, Stage2) or isinstance(organism, Stage3)
    
    def __str__(self):
        return "4"


class Stage5(Animal):
    """Apex Predator - eats all other animal types"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    def can_eat(self, organism: Organism) -> bool:
        """Stage5 animals can eat all other animals but not plants"""
        return isinstance(organism, Animal) and not isinstance(organism, Stage5)
    
    def __str__(self):
        return "5"