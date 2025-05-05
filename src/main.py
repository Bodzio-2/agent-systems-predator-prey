from sim.grid_element import TerrainType, GridElement
from sim.organism import *
from sim.chainy import Chainy
from tkinter import *


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
        self.refresh_window()
        self.window.mainloop()
        
    def refresh_window(self, chainy: Chainy = None) -> None:
        self.canvas.delete("grid_element")

        if not chainy:
            # Test stuff
            grid_el = GridElement(**{'position': (5, 5), 
                                    'terrain': TerrainType.WATER})
            plant = Plant(**{'energy': 10, 
                            'nutrition': 10, 
                            'position': grid_el.position, 
                            'grow_rate': 5})
            stage2 = Stage2(**{'energy': 20, 
                            'nutrition': 30, 
                            'position': grid_el.position, 
                            'speed': 1, 
                            'reproduction_rate': 1, 
                            'reproduction_threshold': 2, 
                            'fov': 3})


            grid_el.organisms.append(stage2)
            grid_el.organisms.append(stage2)
            grid_el.organisms.append(stage2)
            grid_el.organisms.append(plant)


            self.draw_grid_element(grid_el)
        else:
            for col in chainy.grid:
                for grid_el in col:
                    self.draw_grid_element(grid_el)

    

    def create_grid(self) -> None:

        for line in range(0, self.width, 50):
            self.canvas.create_line([(line,0), (line, self.height)], fill='black', tags='grid_line_w')

        for line in range(0, self.height, 50):
            self.canvas.create_line([(0, line), (self.width, line)], fill='black', tags='grid_line_h')
        
        self.canvas.grid(row=0, column=0)


    def draw_grid_element(self, grid_element: GridElement) -> None:
        coords = (grid_element.position[0] * self.grid_square_size, grid_element.position[1] * self.grid_square_size)

        self.canvas.create_rectangle(coords, (coords[0] + self.grid_square_size, coords[1] + self.grid_square_size), fill=TerrainType.colors_dict()[grid_element.terrain], outline='', tags=['grid_element', 'terrain'])

        organism_list = ''

        for organism in grid_element.organisms:
            if isinstance(organism, Plant):
                grass_coords = (coords[0] + self.grid_square_size/5, coords[1] + self.grid_square_size/5)
                self.canvas.create_rectangle(grass_coords, (coords[0] + (self.grid_square_size * 4/5) , coords[1] + (self.grid_square_size * 4/5)), fill='green', outline='', tags=['grid_element', 'plant'])
            elif isinstance(organism, Animal):
                mid_coords = (coords[0] + self.grid_square_size/2, coords[1] + self.grid_square_size/2)
                organism_list += f"{str(organism)}, "

        organism_list = organism_list[:-2]
        self.canvas.create_text(mid_coords, text=organism_list, font=('Helvetica 12 bold'), tags=['grid_element', 'animal'])
        
        self.canvas.tag_lower('plant')
        self.canvas.tag_lower('terrain')
            


window = MainWindow()
