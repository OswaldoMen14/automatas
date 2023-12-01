from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
from agent import *
import json

"""

Code made by Alan Hernández and Oswaldo Mendizábal
30/11/2023

"""
class CityModel(Model):
    """ 
    Creates a model based on a city map.

    Args:
        N: Number of agents in the simulation
    """
    def __init__(self, N, file):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("static/city_files/mapDictionary.json"))

        self.N = N
        self.carInDestination = 0

        self.traffic_lights = []

        self.destination = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open(file) as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            # Create a MultiGrid and RandomActivation scheduler for the model
            self.grid = MultiGrid(self.width, self.height, torus=False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s", "X", "x"]:
                        if col == "S":
                            agent = Traffic_Light(f"tl_{r*self.width+c}", self, False, int(dataDictionary[col]), "S")
                        elif col == "X":
                            agent = Traffic_Light(f"tl_{r*self.width+c}", self, False, int(dataDictionary[col]), "X")
                        elif col == "x":
                            agent = Traffic_Light(f"tl_{r*self.width+c}", self, False, int(dataDictionary[col]), "x")
                        else:
                            agent = Traffic_Light(f"tl_{r*self.width+c}", self, True, int(dataDictionary[col]), "s")
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destination.append((c, self.height - r - 1))

        self.running = True
        self.step_count = 0
        self.car_generateblock = 0

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1
        position = [(0, self.height-1), (self.width - 1, self.height - 1), (0, 0), (self.width - 1, 0)]

        #stops the simulation when step_count == 1000
        if self.step_count == 1000:
            self.running = False

        #adds cars in the simulation any x steps
        elif self.step_count == 1 or self.step_count % self.N == 0:

            #generates cars in the 4 corners of the map
            for i in range(4):
                destination = random.choice(self.destination)
                if not any(isinstance(agent, Car) for agent in self.grid.get_cell_list_contents([position[i]])):
                    car = Car(f"car_{self.step_count}_{i}", self, position[i], destination)
                    self.grid.place_agent(car, position[i])
                    car.initialize_path()
                    self.schedule.add(car)
                    print("new car added to the grid")
                    print("this car is going to: ", destination)
                else:

                    #if blockage, stop the simulation 
                    self.car_generateblock += 1
            if self.car_generateblock == 4:
                self.running = False
            else:
                self.car_generateblock = 0
