from mesa import Agent
import heapq

def heuristic(a, b):
    """
    Returns the Manhattan distance between two cells.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(graph, start, goal, pathclear):
    """
    Finds the shortest path between two cells using A*.
    """
    print(f"Starting A* search from {start} to {goal}")
    obstacles = [] # Priority queue
    heapq.heappush(obstacles, (0, start)) # Add start cell to queue
    wherefrom = {start: None} # Dictionary to keep track of where the path came from
    sofar = {start: 0} # Dictionary to keep track of the cost so far
    
    while not len(obstacles) == 0:
        current = heapq.heappop(obstacles)[1] # Get the cell with the lowest cost
        #print(f"Checking cell: {current}")
        if current == goal: # If the goal is reached, stop
            #print("Goal reached in A* search")
            break
        for next in graph.get_neighborhood(current, moore=False, include_center=False): # Get the neighbors of the current cell
            if not pathclear(current, next): # If the path is not clear,
                continue # Skip this neighbor
            new_cost = sofar[current] + 1 # Calculate the cost to get to the neighbor
            if next not in sofar or new_cost < sofar[next]: # If the neighbor has not been visited or the cost is lower than the previous cost,
                sofar[next] = new_cost # Update the cost
                priority = new_cost + heuristic(goal, next) # Calculate the priority
                heapq.heappush(obstacles, (priority, next)) # Add the neighbor to the queue
                wherefrom[next] = current # Update the path
                
    path = {} # Dictionary to keep track of the path
    current = goal # Start at the goal
    while current != start: # While the start is not reached,
        if current in wherefrom: # If the current cell is in the path,
            prev = wherefrom[current] # Get the previous cell
            path[prev] = current  # Map predecessor to current position
            current = prev # Update the current cell
        else: # If the current cell is not in the path,
            print("No path found in A* search")
            return {}  # Return empty path if no path is found

    print(f"Path found: {path}")
    return path # Return the path

class Car(Agent):
    """
    Agent that moves towards a destination using A*.
    """
    def __init__(self, unique_id, model, spawn, destination = None):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            spawn: Where the agent is spawned
            destination: Where the agent is going
        """
        super().__init__(unique_id, model)
        self.destination = destination
        self.spawn = spawn
        self.path = None
        self.state = "life"
    
    def initialize_path(self):
        """
        Initializes the path for the agent.
        """
        self.path = self.find_path()

    def is_direction_valid(self, current_pos, next_pos, road_direction):
        """
        Checks if moving from current_pos to next_pos is valid based on the road_direction.
        !!!Agregar que solo se puedan mover en diagonal si hay movimiento en la direccion permitida!!!
        """
        dx = next_pos[0] - current_pos[0] # Change in x
        dy = next_pos[1] - current_pos[1] # Change in y
        if road_direction == "Right": # If the road is going right,
            return dx != -1 # Moving left is not allowed
        elif road_direction == "Left": # If the road is going left,
            return dx != 1 # Moving right is not allowed
        elif road_direction == "Up": # If the road is going up,
            return dy != -1 # Moving down is not allowed
        elif road_direction == "Down": # If the road is going down,
            return dy != 1 # Moving up is not allowed
        return False # If the road direction is invalid, return False

    def find_path(self):
        """
        Finds the path from spawn to destination.
        """
        if self.destination: # If the destination is set,
            print(f"Finding path for Car {self.unique_id} from {self.spawn} to {self.destination}")
            def pathclear(current, next): # Function to check if the path is clear
                cell_contents = self.model.grid.get_cell_list_contents([next]) # Get the contents of the next cell

                # Check if the next cell contains an obstacle
                if any(isinstance(agent, Obstacle) for agent in cell_contents):
                    #print(f"Obstacle found at {next}")  # Debug
                    return False

                # Check if the next cell is a road, traffic light, or destination
                if any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in cell_contents):
                    # If it's a road, check the direction
                    roads = [agent for agent in cell_contents if isinstance(agent, Road)]
                    if roads: # If there is a road in the cell
                        road = roads[0]  # Get the first road
                        return self.is_direction_valid(current, next, road.direction) # Check if the direction is valid
                    return True  # If it's a traffic light or destination, movement is allowed
                return False  # Cell without road, traffic light, or destination is not valid
            return a_star_search(self.model.grid, self.spawn, self.destination, pathclear) # Find the path
        print("No destination set for Car, no path to find")  # in case the destination is not reachable or not able to be set
        return None # If the destination is not set, return None
    

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """        
        if self.path and self.pos in self.path:
            next_pos = self.path.get(self.pos)

            if next_pos is not None:
                # Check if the next position is occupied
                cell_contents = self.model.grid.get_cell_list_contents([next_pos])
                
                if not any(isinstance(agent, Car) for agent in cell_contents):
                    # If the next position is not occupied by another car
                    # Check if the next position is a traffic light
                    traffic_lights = [agent for agent in cell_contents if isinstance(agent, Traffic_Light)]

                    if traffic_lights:
                        traffic_light = traffic_lights[0]
                        if traffic_light.state:  # Assumes traffic_light.state is a boolean
                            # Move only if the traffic light is green
                            self.model.grid.move_agent(self, next_pos)
                            self.direction = self.get_direction(self.pos, next_pos)
                            if next_pos == self.destination:
                                print(f"Car {self.unique_id} reached destination {self.destination}")
                                self.model.grid.move_agent(self, next_pos)
                                self.state = "intermediate"
                        else:
                            # If the traffic light is red, the car should wait
                            print(f"Car {self.unique_id} waiting at red traffic light")
                    else:
                        # If there is no traffic light, move freely
                        self.model.grid.move_agent(self, next_pos)
                        self.direction = self.get_direction(self.pos, next_pos)
                        if next_pos == self.destination:
                            print(f"Car {self.unique_id} reached destination {self.destination}")
                            self.model.grid.move_agent(self, next_pos)
                            self.state = "intermediate"
                            
                else:
                    # If the next position is occupied, the car should wait
                    print(f"Car {self.unique_id} waiting for clear path")
            else:
                print("No valid next position found.")
        
    def get_direction(self, current_pos, next_pos):
        """
        Determines the direction the agent should face after moving.
        """
        dx = next_pos[0] - current_pos[0] # Change in x
        dy = next_pos[1] - current_pos[1] # Change in y
        if dx == 1: # If the agent moved right,
            return "Right"
        elif dx == -1: # If the agent moved left,
            return "Left"
        elif dy == -1: # If the agent moved up,
            return "Up"
        elif dy == 1: # If the agent moved down,
            return "Down"
        else: # If the agent didn't move,
            return None

    def step(self): 
        """ 
        Determines the new direction it will take, and then moves
        """
        if self.state == "life":
            self.move()
        elif self.state == "intermediate":
            self.state = "death"
            pass
        elif self.state == "death":
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10,type = None):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange
        self.type = type

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass