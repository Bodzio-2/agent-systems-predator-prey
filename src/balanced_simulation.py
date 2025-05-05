from sim.chainy import Chainy
from sim.organism import *
from sim.grid_element import *
import random

def run_balanced_simulation():

    sim = Chainy()
    

    grid_size = 30
    sim.init_grid(width=grid_size, height=grid_size)
    

    original_move = Animal.move
    def energy_efficient_move(self, direction):
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)

        self.position = (x + dx, y + dy)

        self.energy -= (abs(dx) + abs(dy)) * 0.3  # Even lower movement cost
    Animal.move = energy_efficient_move
    

    original_grow = Plant.grow
    def controlled_grow(self, sunlight=0):
        growth = max(1, int(sunlight * self.grow_rate * 0.4))  
        self.energy += growth
        self.nutrition += growth // 2
    Plant.grow = controlled_grow
    

    original_reproduce = Animal.reproduce
    def enhanced_reproduce(self):
        original_threshold = self.reproduction_threshold
        self.reproduction_threshold = self.reproduction_threshold * 0.6
        result = original_reproduce(self)
        self.reproduction_threshold = original_threshold
        return result
    Animal.reproduce = enhanced_reproduce
    
    # POPULATE THE WORLD
    
    plant_positions = []
    for _ in range(80):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        if (x, y) in plant_positions:
            continue
        plant_positions.append((x, y))
        sim.add_organism("plant", (x, y), 
                        energy=random.randint(20, 40),
                        nutrition=random.randint(15, 25),
                        grow_rate=random.uniform(0.2, 0.4))
    

    for _ in range(70):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage2", (x, y), 
                        energy=200,
                        nutrition=40,
                        reproduction_rate=0.2,
                        reproduction_threshold=70,
                        speed=2)
    

    for _ in range(25):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage3", (x, y),
                        energy=180,
                        nutrition=35,
                        reproduction_rate=0.15,
                        reproduction_threshold=90,
                        speed=2)
    

    for _ in range(10):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage4", (x, y),
                        energy=220,
                        nutrition=45,
                        reproduction_rate=0.1,
                        reproduction_threshold=110,
                        speed=2)
    

    for _ in range(5):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage5", (x, y), 
                        energy=250,
                        reproduction_rate=0.05,
                        reproduction_threshold=150,
                        speed=3)
    
    # Run the simulation for many steps
    print("Starting balanced simulation...")
    history = [] 
    
    for i in range(100):  

        sim.update()
        
        counts = sim.get_organism_counts()
        history.append(counts.copy())
        
        if i % 10 == 0 or i == 99:
            print(f"\nTime step: {i}")
            print(f"Plants: {counts['plant']}")
            print(f"Herbivores (Stage2): {counts['stage2']}")
            print(f"Omnivores (Stage3): {counts['stage3']}")
            print(f"Carnivores (Stage4): {counts['stage4']}")
            print(f"Apex Predators (Stage5): {counts['stage5']}")


    print("\nPopulation summary:")
    print("Time  | Plants | Stage2 | Stage3 | Stage4 | Stage5")
    print("------+--------+--------+--------+--------+-------")
    for i in range(0, 100, 10):
        c = history[i]
        print(f"{i:4d}  | {c['plant']:6d} | {c['stage2']:6d} | {c['stage3']:6d} | {c['stage4']:6d} | {c['stage5']:5d}")
    
    final = history[-1]
    print(f"\nFinal stats (step 99):")
    print(f"Plants: {final['plant']}")
    print(f"Herbivores: {final['stage2']}")
    print(f"Omnivores: {final['stage3']}")
    print(f"Carnivores: {final['stage4']}")
    print(f"Apex Predators: {final['stage5']}")
    
    Animal.move = original_move
    Plant.grow = original_grow
    Animal.reproduce = original_reproduce

if __name__ == "__main__":
    run_balanced_simulation()
