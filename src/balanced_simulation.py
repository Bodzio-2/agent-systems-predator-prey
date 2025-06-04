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

def run_balanced_simulation(max_steps=5000):
    sim = Chainy()
    grid_size = 30
    all_snapshots = []
    sim.init_grid(width=grid_size, height=grid_size)



    INIT_APEX = 25
    INIT_CARNIVORES = 30
    INIT_OMNIVORES = 30
    INIT_HERBIVORES = 20
    INIT_PLANTS = 15


    POP_FLOOR = {'plant': 3, 'stage2': 5, 'stage3': 14, 'stage4': 18, 'stage5': 18}
    POP_CAP =   {'plant': 20, 'stage2': 28, 'stage3': 38, 'stage4': 44, 'stage5': 44}


    original_move = Animal.move
    def energy_efficient_move(self, direction):
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)

        new_x = x + dx
        new_y = y + dy


        grid_width, grid_height = sim.size
        new_x = max(0, min(new_x, grid_width - 1))
        new_y = max(0, min(new_y, grid_height - 1))

        self.position = (new_x, new_y)

        base_cost = (abs(dx) + abs(dy)) * 0.15
        if isinstance(self, Stage4):
            base_cost *= 1.4
        elif isinstance(self, Stage5):
            base_cost *= 1.2
        self.energy -= base_cost
    Animal.move = energy_efficient_move


    original_grow = Plant.grow
    def controlled_grow(self, sunlight=0):
        growth = max(1, int(sunlight * self.grow_rate * 0.05))
        self.energy += growth
        self.nutrition += growth // 2
    Plant.grow = controlled_grow


    original_reproduce = Animal.reproduce
    def enhanced_reproduce(self):

        if not hasattr(sim, '_original_remove_organism'):
            sim._original_remove_organism = sim.remove_organism
        def safe_remove_organism(org):
            typ = org.__class__.__name__.lower()
            counts = sim.get_organism_counts()
            floor = POP_FLOOR.get(typ, 0)
            if counts[typ] > floor:
                sim._original_remove_organism(org)
            else:

                if hasattr(org, 'energy'):
                    org.energy = max(org.energy, 60)
                if hasattr(org, 'nutrition'):
                    org.nutrition = max(getattr(org, 'nutrition', 0), 30)
        sim.remove_organism = safe_remove_organism


        counts = sim.get_organism_counts()
        typ = self.__class__.__name__.lower()
        cap = POP_CAP.get(typ, 500)
        floor = POP_FLOOR.get(typ, 0)
        if counts[typ] >= cap:
            return None

        if counts[typ] <= floor:

            self.energy += self.reproduction_threshold
        original_threshold = self.reproduction_threshold

        import random
        jitter = random.uniform(0.95, 1.05)
        if isinstance(self, Stage5):
            self.reproduction_threshold = self.reproduction_threshold * 0.10 * jitter  # apex: much easier to reproduce
        elif typ == 'stage4':
            self.reproduction_threshold = self.reproduction_threshold * 0.09 * jitter  # carnivore: much easier
        elif typ == 'stage3':
            self.reproduction_threshold = self.reproduction_threshold * 0.16 * jitter  # omnivore: easier
        elif typ == 'stage2':
            self.reproduction_threshold = self.reproduction_threshold * 0.24 * jitter  # herbivore: easier
        else:
            self.reproduction_threshold = self.reproduction_threshold * 0.33 * jitter
        result = original_reproduce(self)
        self.reproduction_threshold = original_threshold
        return result
    Animal.reproduce = enhanced_reproduce


    original_eat = Animal.eat
    def logical_trophic_eat(self, other):

        if isinstance(other, Plant):
            gained_energy = other.get_nutrition()
            if isinstance(self, Stage2):
                gained_energy *= 1.5
            self.energy += gained_energy
        elif isinstance(other, Animal):


            import random
            predation_jitter = random.uniform(0.8, 1.05)

            prey_typ = other.__class__.__name__.lower()
            prey_floor = POP_FLOOR.get(prey_typ, 0)
            prey_count = sim.get_organism_counts()[prey_typ]
            if prey_count <= prey_floor:
                return
            if isinstance(self, Stage5):
                gained_energy = int(other.energy * 0.22 * predation_jitter)
            elif isinstance(self, Stage4):
                gained_energy = int(other.energy * 0.22 * predation_jitter)
            elif isinstance(self, Stage3):
                gained_energy = int(other.energy * 0.13 * predation_jitter)
            elif isinstance(self, Stage2):
                gained_energy = int(other.energy * 0.09 * predation_jitter)
            else:
                gained_energy = int(other.energy * 0.05 * predation_jitter)
            self.energy += gained_energy
        else:
            self.energy += other.get_nutrition()
        sim.remove_organism(other)
    Animal.eat = logical_trophic_eat




    plant_positions = []
    for _ in range(INIT_PLANTS):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        if (x, y) in plant_positions:
            continue
        plant_positions.append((x, y))
        sim.add_organism("plant", (x, y),
                         energy=random.randint(25, 45),
                         nutrition=random.randint(18, 30),
                         grow_rate=random.uniform(0.25, 0.35))


    for _ in range(INIT_HERBIVORES):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage2", (x, y),
                         energy=520,
                         nutrition=60,
                         reproduction_rate=random.uniform(0.35, 0.45),
                         reproduction_threshold=40,
                         speed=2)


    for _ in range(INIT_OMNIVORES):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage3", (x, y),
                         energy=230,
                         nutrition=35,
                         reproduction_rate=random.uniform(0.13, 0.22),
                         reproduction_threshold=90,
                         speed=2)


    for _ in range(INIT_CARNIVORES):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage4", (x, y),
                         energy=140,
                         nutrition=40,
                         reproduction_rate=random.uniform(0.09, 0.17),
                         reproduction_threshold=140,
                         speed=2)


    for _ in range(INIT_APEX):
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
        sim.add_organism("stage5", (x, y),
                         energy=200,
                         reproduction_rate=random.uniform(0.16, 0.22),  # Higher reproduction rate
                         reproduction_threshold=90,  # Lower threshold
                         speed=3)


    print("Starting enhanced, infinite simulation with 10% energy rule...\n")
    history = []
    i = 0
    for step in range(max_steps):
        sim.update()



        counts = sim.get_organism_counts()
        for typ, floor in POP_FLOOR.items():
            deficit = floor - counts.get(typ, 0)
            if deficit > 0:
                for _ in range(deficit):
    
                    pos = (random.randint(0, grid_size-1), random.randint(0, grid_size-1))
                    if typ == 'plant':
                        sim.add_organism('plant', pos, energy=30, nutrition=20, grow_rate=random.uniform(0.25, 0.35))
                    elif typ == 'stage2':
                        sim.add_organism('stage2', pos, energy=70, nutrition=25, reproduction_rate=random.uniform(0.1,0.2), reproduction_threshold=60, speed=2)
                    elif typ == 'stage3':
                        sim.add_organism('stage3', pos, energy=90, nutrition=30, reproduction_rate=random.uniform(0.05,0.2), reproduction_threshold=80, speed=2)
                    elif typ == 'stage4':
                        sim.add_organism('stage4', pos, energy=120, nutrition=38, reproduction_rate=random.uniform(0,0.1), reproduction_threshold=110, speed=2)
                    elif typ == 'stage5':
                        sim.add_organism('stage5', pos, energy=200, reproduction_rate=random.uniform(0.1,0.2), reproduction_threshold=90, speed=3)

        counts = sim.get_organism_counts()
        for org in sim.organisms:
            typ = org.__class__.__name__.lower()
            if counts.get(typ, 0) <= POP_FLOOR.get(typ, 0):
                if hasattr(org, 'energy'):
                    org.energy = max(org.energy, 60)
                if hasattr(org, 'nutrition'):
                    org.nutrition = max(getattr(org, 'nutrition', 0), 30)


        counts = sim.get_organism_counts()
        snapshot = {k: counts.get(k, 0) for k in ['plant', 'stage2', 'stage3', 'stage4', 'stage5']}
        history.append(snapshot)
        snapshot_dict = sim.get_dict()
        all_snapshots.append(snapshot_dict)
        if step % 10 == 0:
            print(f"\nTime step: {step}")
            print(f"Plants: {counts['plant']}")
            print(f"Herbivores (Stage2): {counts['stage2']}")
            print(f"Omnivores (Stage3): {counts['stage3']}")
            print(f"Carnivores (Stage4): {counts['stage4']}")
            print(f"Apex Predators (Stage5): {counts['stage5']}")


        if all(counts[k] == 0 for k in ['plant', 'stage2', 'stage3', 'stage4', 'stage5']):
            print("All organisms have died. Simulation ended.")
            break
    else:
        print(f"\nReached max_steps = {max_steps}. Simulation ended.")


    with open("population_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("\nPopulation history saved to population_history.json.")

    print("\nAll organisms have died or max steps reached. Simulation ended.")
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

    # plot_simulation(history)
if __name__ == "__main__":
    # Fine-tuned for a 500-step run
    run_balanced_simulation(max_steps=500)
