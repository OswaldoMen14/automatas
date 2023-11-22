from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
from agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []

        self.destination = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
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

        self.num_agents = N
        self.running = True
        self.step_count = 0

        def remove_car(self, agent):
            """
            Remove a car from the model.
            """
            self.schedule.remove(agent) # Remove the agent from the scheduler
            self.grid.remove_agent(agent) # Remove the agent from the grid

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1

        if self.step_count == 1 or self.step_count % 10 == 0:
            destination = random.choice(self.destination)
            car1 = Car(f"car_{self.step_count}_1", self, (0, self.height-1), destination)
            self.grid.place_agent(car1, (0, self.height - 1))
            car1.initialize_path()  # Initialize the path after placing the car
            self.schedule.add(car1)
            
            print("new car added to the grid")
            print("this car is going to: ", destination)



            destination = random.choice(self.destination)
            car2 = Car(f"car_{self.step_count}_2", self,(self.width - 1, self.height - 1) , destination)
            self.grid.place_agent(car2, (self.width - 1, self.height - 1))
            car2.initialize_path()  # Initialize the path after placing the car
            self.schedule.add(car2)
            print("new car added to the grid")
            print("this car is going to: ", destination)

            
            destination = random.choice(self.destination)
            car3 = Car(f"car_{self.step_count}_3", self, (0, 0) ,destination)
            self.grid.place_agent(car3, (0, 0))
            car3.initialize_path()  # Initialize the path after placing the car
            self.schedule.add(car3)
            print("new car added to the grid")
            print("this car is going to: ", destination)

            destination = random.choice(self.destination)
            car4 = Car(f"car_{self.step_count}_4", self,(self.width - 1, 0) , destination)
            self.grid.place_agent(car4, (self.width - 1, 0))
            car4.initialize_path()  # Initialize the path after placing the car
            self.schedule.add(car4)
            print("new car added to the grid")
            print("this car is going to: ", destination)