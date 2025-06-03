from sim.chainy import Chainy
from sim.organism import *
from sim.grid_element import *
import random
import os
import json
import datetime
import matplotlib.pyplot as plt

def plot_simulation(history):
    time_steps = list(range(len(history)))
    plant_counts = [h['plant'] for h in history]
    stage2_counts = [h['stage2'] for h in history]
    stage3_counts = [h['stage3'] for h in history]
    stage4_counts = [h['stage4'] for h in history]
    stage5_counts = [h['stage5'] for h in history]

    # --- Plot 1: Line chart ---
    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, plant_counts, label='Plants', color='green')
    plt.plot(time_steps, stage2_counts, label='Stage2 (Herbivores)', color='orange')
    plt.plot(time_steps, stage3_counts, label='Stage3 (Omnivores)', color='blue')
    plt.plot(time_steps, stage4_counts, label='Stage4 (Carnivores)', color='red')
    plt.plot(time_steps, stage5_counts, label='Stage5 (Apex Predators)', color='purple')
    plt.xlabel("Time Step")
    plt.ylabel("Population")
    plt.title("Population of Each Organism Type Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("population_line_chart.png")
    plt.show()

    # --- Plot 2: Stacked Area Chart ---
    plt.figure(figsize=(10, 6))
    plt.stackplot(time_steps, plant_counts, stage2_counts, stage3_counts,
                  stage4_counts, stage5_counts,
                  labels=['Plants', 'Stage2', 'Stage3', 'Stage4', 'Stage5'],
                  colors=['green', 'orange', 'blue', 'red', 'purple'])
    plt.xlabel("Time Step")
    plt.ylabel("Total Population")
    plt.title("Ecosystem Composition Over Time")
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig("ecosystem_area_chart.png")
    plt.show()

def run_balanced_simulation():
    sim = Chainy()
    grid_size = 30
    all_snapshots = []
    sim.init_grid(width=grid_size, height=grid_size)

    # Modify Animal.move
    original_move = Animal.move
    def energy_efficient_move(self, direction):
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)

        new_x = x + dx
        new_y = y + dy

        # Clamp within bounds
        grid_width, grid_height = sim.size
        new_x = max(0, min(new_x, grid_width - 1))
        new_y = max(0, min(new_y, grid_height - 1))

        self.position = (new_x, new_y)
        self.energy -= (abs(dx) + abs(dy)) * 0.15
    Animal.move = energy_efficient_move

    # Modify Plant.grow (slightly buffed)
    original_grow = Plant.grow
    def controlled_grow(self, sunlight=0):
        growth = max(2, int(sunlight * self.grow_rate * 0.2))
        self.energy += growth
        self.nutrition += growth // 2
    Plant.grow = controlled_grow

    # Modify Animal.reproduce
    original_reproduce = Animal.reproduce
    def enhanced_reproduce(self):
        # if sim.get_organism_counts()['stage2'] > 300:
        #     return None
        if sim.get_organism_counts()[self.__class__.__name__.lower()] > 2000:
            return None
        original_threshold = self.reproduction_threshold
        self.reproduction_threshold = self.reproduction_threshold * 0.5
        result = original_reproduce(self)
        self.reproduction_threshold = original_threshold
        return result
    Animal.reproduce = enhanced_reproduce


    original_eat = Animal.eat
    def ten_percent_eat(self, other):
        if other.energy > 0:
            gained_energy = int(other.energy * 0.1)
            self.energy += gained_energy
        else:
            self.energy += 1  
        sim.remove_organism(other)
    Animal.eat = ten_percent_eat

    # Populate grid
    plant_positions = []
    for _ in range(80):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        if (x, y) in plant_positions:
            continue
        plant_positions.append((x, y))
        sim.add_organism("plant", (x, y),
                         energy=random.randint(20, 40),
                         nutrition=random.randint(15, 25),
                         grow_rate=random.uniform(0.2, 0.3))

    # Buffed herbivores
    for _ in range(70):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage2", (x, y),
                         energy=380,
                         nutrition=50,
                         reproduction_rate=random.uniform(0.2, 0.3),
                         reproduction_threshold=50,
                         speed=2)

    # Buffed omnivores
    for _ in range(25):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage3", (x, y),
                         energy=150,
                         nutrition=30,
                         reproduction_rate=random.uniform(0.1, 0.2),
                         reproduction_threshold=100,
                         speed=2)

    # Normal carnivores
    for _ in range(10):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage4", (x, y),
                         energy=160,
                         nutrition=45,
                         reproduction_rate=random.uniform(0.1, 0.2),
                         reproduction_threshold=130,
                         speed=2)

    # Apex predators
    for _ in range(5):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage5", (x, y),
                         energy=220,
                         reproduction_rate=random.uniform(0.1, 0.2),
                         reproduction_threshold=130,
                         speed=3)

    # Run the simulation
    print("Starting enhanced, infinite simulation with 10% energy rule...\n")
    history = []
    i = 0
    while True:
        sim.update()
        counts = sim.get_organism_counts()
        history.append(counts.copy())
        snapshot_dict = sim.get_dict()
        all_snapshots.append(snapshot_dict)
        # Stop if any organism count reaches zero
        if sum(1 for count in counts.values() if count == 0) >= 2:
            print(f"Stopping simulation at timestep {i} because an organism type went extinct.")
            break

        if i % 10 == 0:
            print(f"\nTime step: {i}")
            print(f"Plants: {counts['plant']}")
            print(f"Herbivores (Stage2): {counts['stage2']}")
            print(f"Omnivores (Stage3): {counts['stage3']}")
            print(f"Carnivores (Stage4): {counts['stage4']}")
            print(f"Apex Predators (Stage5): {counts['stage5']}")
        i += 1


    print("\nAll organisms have died. Simulation ended.")
    print("Population summary (every 10 steps):")
    print("Time  | Plants | Stage2 | Stage3 | Stage4 | Stage5")
    print("------+--------+--------+--------+--------+-------")
    for j in range(0, len(history), 10):
        c = history[j]
        print(f"{j:4d}  | {c['plant']:6d} | {c['stage2']:6d} | {c['stage3']:6d} | {c['stage4']:6d} | {c['stage5']:5d}")

    # Restore original methods
    Animal.move = original_move
    Plant.grow = original_grow
    Animal.reproduce = original_reproduce
    Animal.eat = original_eat

    with open("simulation_full_run.json", "w") as f:
        json.dump(all_snapshots, f, indent=2)

    plot_simulation(history)
if __name__ == "__main__":
    run_balanced_simulation()
