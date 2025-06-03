from sim.organism import *
from sim.grid_element import *

class Chainy:
    def __init__(self):
        self.organisms: list[Organism] = []
        self.grid: list[list[GridElement]] = []
        self.size: tuple[int, int] = (0,0)
        self.time_step: int = 0
        self.sim_speed: float = 1
        self.stats: list[float] = []

    def get_dict(self) -> dict:
        # initial_dict = vars(self)
        initial_dict = {
            'size_x': self.size[0],
            'size_y': self.size[1],
            'time_step': self.time_step,
            'sim_speed': self.sim_speed,
            'stats': self.stats
        }
        # initial_dict['organisms'] = [i.get_dict() for i in self.organisms]
        initial_dict['grid'] = [[j.get_dict() for j in i] for i in self.grid]
        return initial_dict

    def init_grid(self, width: int = 50, height: int = 50) -> None:
        import random
        self.size = (width, height)
        self.grid = []
        
        for y in range(height):
            row = []
            for x in range(width):
                terrain_roll = random.random()
                if terrain_roll < 0.1:
                    terrain = TerrainType.ROCK
                elif terrain_roll < 0.25:
                    terrain = TerrainType.WATER
                else:
                    terrain = TerrainType.DIRT
                    
                grid_element = GridElement(position=(x, y), terrain=terrain)
                
                sunlight = max(1, int(10 * (height - y) / height))
                grid_element.update_sunlight(sunlight)
                
                row.append(grid_element)
            self.grid.append(row)
        
        self.spawn_plants(initial_count=int(width * height * 0.1))
        
    def update(self) -> None:
        import random
        self.time_step += 1
        
        current_organisms = self.organisms.copy()
        new_organisms = []
        organisms_to_remove = []
        
        for organism in current_organisms:
            if organism.get_energy() <= 0:
                organisms_to_remove.append(organism)
                continue
                
            x, y = organism.get_position()
            if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
                organisms_to_remove.append(organism)
                continue
                
            current_element = self.grid[y][x]
            
            if isinstance(organism, Plant):
                organism.grow(current_element.sunlight_lvl)
                
                if random.random() < 0.05 and organism.get_energy() > 50:
                    for _ in range(5):
                        dx, dy = random.randint(-1, 1), random.randint(-1, 1)
                        new_x, new_y = x + dx, y + dy
                        
                        if (0 <= new_x < self.size[0] and 0 <= new_y < self.size[1] and
                            self.grid[new_y][new_x].terrain == TerrainType.DIRT and
                            len(self.grid[new_y][new_x].organisms) < 3):
                                
                            new_plant = Plant(
                                energy=organism.get_energy() // 3,
                                nutrition=organism.get_nutrition() // 2,
                                position=(new_x, new_y),
                                grow_rate=organism.grow_rate
                            )
                            new_organisms.append(new_plant)
                            self.grid[new_y][new_x].add_organism(new_plant)
                            organism.energy -= organism.get_energy() // 3
                            break
                    
            elif isinstance(organism, Animal):
                organism.energy -= 0.5
                
                visible_organisms = []
                for dy in range(-organism.fov, organism.fov + 1):
                    for dx in range(-organism.fov, organism.fov + 1):
                        check_x, check_y = x + dx, y + dy
                        if (0 <= check_x < self.size[0] and 0 <= check_y < self.size[1]):
                            visible_organisms.extend(self.grid[check_y][check_x].organisms)
                            
                if hasattr(organism, 'can_eat'):
                    potential_food = [o for o in visible_organisms 
                                     if o != organism and organism.can_eat(o)]
                else:
                    potential_food = []
                    
                if potential_food:
                    target = min(potential_food, key=lambda o: 
                                abs(o.get_position()[0] - x) + abs(o.get_position()[1] - y))
                    
                    tx, ty = target.get_position()
                    move_dir = (max(min(tx - x, 1), -1), max(min(ty - y, 1), -1))
                    
                    organism.move(move_dir)
                    
                    new_x, new_y = organism.get_position()
                    if current_element.position != (new_x, new_y):
                        if 0 <= new_x < self.size[0] and 0 <= new_y < self.size[1]:
                            current_element.kill_organism(organism)
                            self.grid[new_y][new_x].add_organism(organism)
                            
                    if organism.get_position() == target.get_position():
                        new_x, new_y = organism.get_position()
                        if not (0 <= new_x < self.size[0] and 0 <= new_y < self.size[1]):
                            continue
                            
                        can_consume = True
                        if isinstance(target, Animal):
                            can_consume = not target.flee_chance(organism)
                            
                        if can_consume:
                            organism.eat(target)
                            organisms_to_remove.append(target)
                            self.grid[new_y][new_x].kill_organism(target)
                            
                else:
                    if random.random() < 0.4:
                        move_dir = (random.randint(-1, 1), random.randint(-1, 1))
                        organism.move(move_dir)
                        
                        new_x, new_y = organism.get_position()
                        if current_element.position != (new_x, new_y):
                            if 0 <= new_x < self.size[0] and 0 <= new_y < self.size[1]:
                                current_element.kill_organism(organism)
                                self.grid[new_y][new_x].add_organism(organism)
                    
                reproduction_chance = organism.reproduction_rate
                if isinstance(organism, Stage2):
                    reproduction_chance *= 1.3
                
                if random.random() < reproduction_chance and organism.get_energy() > organism.reproduction_threshold:
                    offspring = organism.reproduce()
                    if offspring:
                        for _ in range(8):
                            dx, dy = random.randint(-1, 1), random.randint(-1, 1)
                            new_x, new_y = x + dx, y + dy
                            
                            if (0 <= new_x < self.size[0] and 0 <= new_y < self.size[1] and
                                self.grid[new_y][new_x].terrain != TerrainType.ROCK):
                                
                                offspring.position = (new_x, new_y)
                                new_organisms.append(offspring)
                                self.grid[new_y][new_x].add_organism(offspring)
                                break
        
        for organism in organisms_to_remove:
            if organism in self.organisms:
                self.organisms.remove(organism)
                
        self.organisms.extend(new_organisms)
        
        if self.time_step % 10 == 0:
            plant_count = sum(1 for organism in self.organisms if isinstance(organism, Plant))
            if plant_count < self.size[0] * self.size[1] * 0.15:
                self.spawn_plants(initial_count=int(self.size[0] * self.size[1] * 0.05))
                
        self.generate_stats()
        
    def spawn_plants(self, initial_count: int = 10) -> None:
        import random
        width, height = self.size
        count = 0
        
        attempts = 0
        max_attempts = initial_count * 3
        
        while count < initial_count and attempts < max_attempts:
            attempts += 1
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            
            if (self.grid[y][x].terrain == TerrainType.DIRT and 
                len(self.grid[y][x].organisms) < 3):
                
                plant = Plant(
                    energy=random.randint(10, 30),
                    nutrition=random.randint(5, 15),
                    position=(x, y),
                    grow_rate=random.uniform(0.1, 0.3)
                )
                
                self.organisms.append(plant)
                self.grid[y][x].add_organism(plant)
                count += 1
                
    def remove_organism(self, organism):
        """Remove organism from simulation."""
        x, y = organism.get_position()
        if (x, y) in self.grid:  # or however you're tracking them
            del self.grid[(x, y)]
    
    def generate_stats(self) -> None:
        plant_count = sum(1 for org in self.organisms if isinstance(org, Plant))
        stage2_count = sum(1 for org in self.organisms if isinstance(org, Stage2))
        stage3_count = sum(1 for org in self.organisms if isinstance(org, Stage3))
        stage4_count = sum(1 for org in self.organisms if isinstance(org, Stage4))
        stage5_count = sum(1 for org in self.organisms if isinstance(org, Stage5))
        
        plant_energy = sum(org.get_energy() for org in self.organisms if isinstance(org, Plant))
        plant_avg_energy = plant_energy / plant_count if plant_count > 0 else 0
        
        animal_energy = sum(org.get_energy() for org in self.organisms if isinstance(org, Animal))
        animal_count = stage2_count + stage3_count + stage4_count + stage5_count
        animal_avg_energy = animal_energy / animal_count if animal_count > 0 else 0
        
        self.stats = [
            self.time_step,
            plant_count,
            stage2_count,
            stage3_count,
            stage4_count,
            stage5_count,
            plant_avg_energy,
            animal_avg_energy
        ]
        
    def display(self) -> None:
        pass
    
    def add_organism(self, organism_type: str, position: tuple[int, int], **kwargs) -> None:
        x, y = position
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
            return
            
        if organism_type == "plant":
            organism = Plant(
                energy=kwargs.get('energy', 20),
                nutrition=kwargs.get('nutrition', 10),
                position=position,
                grow_rate=kwargs.get('grow_rate', 0.2)
            )
        elif organism_type == "stage2":
            organism = Stage2(
                energy=kwargs.get('energy', 50),
                nutrition=kwargs.get('nutrition', 25),
                position=position,
                speed=kwargs.get('speed', 1),
                reproduction_rate=kwargs.get('reproduction_rate', 0.05),
                reproduction_threshold=kwargs.get('reproduction_threshold', 100),
                fov=kwargs.get('fov', 3)
            )
        elif organism_type == "stage3":
            organism = Stage3(
                energy=kwargs.get('energy', 70),
                nutrition=kwargs.get('nutrition', 35),
                position=position,
                speed=kwargs.get('speed', 2),
                reproduction_rate=kwargs.get('reproduction_rate', 0.04),
                reproduction_threshold=kwargs.get('reproduction_threshold', 120),
                fov=kwargs.get('fov', 4)
            )
        elif organism_type == "stage4":
            organism = Stage4(
                energy=kwargs.get('energy', 100),
                nutrition=kwargs.get('nutrition', 50),
                position=position,
                speed=kwargs.get('speed', 2),
                reproduction_rate=kwargs.get('reproduction_rate', 0.03),
                reproduction_threshold=kwargs.get('reproduction_threshold', 150),
                fov=kwargs.get('fov', 5)
            )
        elif organism_type == "stage5":
            organism = Stage5(
                energy=kwargs.get('energy', 150),
                nutrition=kwargs.get('nutrition', 75),
                position=position,
                speed=kwargs.get('speed', 3),
                reproduction_rate=kwargs.get('reproduction_rate', 0.02),
                reproduction_threshold=kwargs.get('reproduction_threshold', 200),
                fov=kwargs.get('fov', 6)
            )
        else:
            return
            
        self.organisms.append(organism)
        self.grid[y][x].add_organism(organism)
        
    def get_organism_counts(self) -> dict:
        counts = {
            'plant': sum(1 for org in self.organisms if isinstance(org, Plant)),
            'stage2': sum(1 for org in self.organisms if isinstance(org, Stage2)),
            'stage3': sum(1 for org in self.organisms if isinstance(org, Stage3)),
            'stage4': sum(1 for org in self.organisms if isinstance(org, Stage4)),
            'stage5': sum(1 for org in self.organisms if isinstance(org, Stage5))
        }
        return counts

    def get_organism_total_count(self) -> int:
        total_count = sum(1 for org in self.organisms if isinstance(org, (Plant, Stage2, Stage3, Stage4, Stage5)))
        return total_count