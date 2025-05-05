from sim.grid_element import TerrainType, GridElement
from sim.organism import *
from sim.chainy import Chainy
from tkinter import *
import random
import time


class MainWindow:

    def __init__(self, grid_height: int = 20, grid_width: int = 20, grid_square_size: int = 50) -> None:
        self.grid_height: int = grid_height
        self.grid_width: int = grid_width
        self.grid_square_size: int = grid_square_size

        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("Food chain simulation")

        self.width = self.grid_square_size * self.grid_width
        self.height = self.grid_square_size * self.grid_height
        self.canvas = Canvas(self.window, background='white', width=self.width, height=self.height)

        self.create_grid()
        self.canvas.grid(row=0, column=0)

    def refresh_window(self, chainy: Chainy = None) -> None:
        self.canvas.delete("grid_element")

        if not chainy:
            return
        else:
            for col in chainy.grid:
                for grid_el in col:
                    self.draw_grid_element(grid_el)

    def create_grid(self) -> None:
        for line in range(0, self.width, self.grid_square_size):
            self.canvas.create_line([(line, 0), (line, self.height)], fill='black', tags='grid_line_w')

        for line in range(0, self.height, self.grid_square_size):
            self.canvas.create_line([(0, line), (self.width, line)], fill='black', tags='grid_line_h')

    def draw_grid_element(self, grid_element: GridElement) -> None:
        coords = (grid_element.position[0] * self.grid_square_size, grid_element.position[1] * self.grid_square_size)

        self.canvas.create_rectangle(coords,
                                     (coords[0] + self.grid_square_size, coords[1] + self.grid_square_size),
                                     fill=TerrainType.colors_dict()[grid_element.terrain],
                                     outline='', tags=['grid_element', 'terrain'])

        organism_list = ''

        for organism in grid_element.organisms:
            if isinstance(organism, Plant):
                grass_coords = (coords[0] + self.grid_square_size / 5, coords[1] + self.grid_square_size / 5)
                self.canvas.create_rectangle(grass_coords,
                                             (coords[0] + (self.grid_square_size * 4 / 5),
                                              coords[1] + (self.grid_square_size * 4 / 5)),
                                             fill='green', outline='', tags=['grid_element', 'plant'])
            elif isinstance(organism, Animal):
                mid_coords = (coords[0] + self.grid_square_size / 2, coords[1] + self.grid_square_size / 2)
                organism_list += f"{str(organism)}, "

        if organism_list:
            organism_list = organism_list[:-2]
            self.canvas.create_text(mid_coords, text=organism_list, font=('Helvetica 12 bold'),
                                    tags=['grid_element', 'animal'])

        self.canvas.tag_lower('plant')
        self.canvas.tag_lower('terrain')

    def run_simulation_step(self, sim: Chainy, max_steps=100, delay=1000000000, step=0):
        if step >= max_steps:
            return
        sim.update()
        self.refresh_window(sim)
        self.window.after(delay, lambda: self.run_simulation_step(sim, max_steps, delay, step + 1))

    def run(self):
        self.window.mainloop()


def run_balanced_simulation_with_gui():
    sim = Chainy()
    grid_size = 20
    sim.init_grid(width=grid_size, height=grid_size)

    original_move = Animal.move
    def energy_efficient_move(self, direction):
        x, y = self.position
        dx, dy = direction
        dx = max(min(dx, self.speed), -self.speed)
        dy = max(min(dy, self.speed), -self.speed)
        self.position = (x + dx, y + dy)
        self.energy -= (abs(dx) + abs(dy)) * 0.3
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

    plant_positions = []
    for _ in range(10):
        
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        if (x, y) in plant_positions:
            continue
        plant_positions.append((x, y))
        sim.add_organism("plant", (x, y),
                         energy=random.randint(20, 40),
                         nutrition=random.randint(15, 25),
                         grow_rate=random.uniform(0.2, 0.4))

    for _ in range(20):
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        sim.add_organism("stage2", (x, y),
                         energy=200,
                         nutrition=40,
                         reproduction_rate=0.2,
                         reproduction_threshold=70,
                         speed=2)

    for _ in range(20):
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        sim.add_organism("stage3", (x, y),
                         energy=180,
                         nutrition=35,
                         reproduction_rate=0.15,
                         reproduction_threshold=90,
                         speed=2)

    for _ in range(10):
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        sim.add_organism("stage4", (x, y),
                         energy=220,
                         nutrition=45,
                         reproduction_rate=0.1,
                         reproduction_threshold=110,
                         speed=2)

    for _ in range(5):
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        sim.add_organism("stage5", (x, y),
                         energy=250,
                         reproduction_rate=0.05,
                         reproduction_threshold=150,
                         speed=3)

    print("Starting simulation with GUI...")

    window = MainWindow(grid_height=grid_size, grid_width=grid_size, grid_square_size=25)
    window.run_simulation_step(sim, max_steps=100, delay=1000)
    window.run()


if __name__ == "__main__":
    run_balanced_simulation_with_gui()
