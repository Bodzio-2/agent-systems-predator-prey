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
        """
        Move the animal in the specified direction
        direction: (dx, dy) tuple indicating the direction to move
        """
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)
        self.position = (x + dx, y + dy)
        self.energy -= (abs(dx) + abs(dy)) * 0.5

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

    def consume(self, food: Organism) -> None:
        """
        Consume another organism to gain energy
        food: the organism to consume
        """

        gained_energy = food.get_nutrition()
        
        if isinstance(self, Stage2) and isinstance(food, Plant):
            gained_energy *= 1.5 
            
        self.energy += gained_energy

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
    
    def grow(self, sunlight: int = 0) -> None:
        """Increase the plant's energy and nutrition based on sunlight and grow rate"""
        growth = max(1, int(sunlight * self.grow_rate * 0.6))  
        self.energy += growth
        self.nutrition += growth // 2  


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