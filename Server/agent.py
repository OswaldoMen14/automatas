from mesa import Agent
import heapq
"""

Code made by Alan Hernández and Oswaldo Mendizábal
30/11/2023

"""
def heuristic(a, b):
    """
    Returns the Manhattan distance between two cells.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(graph, start, goal, pathclear):
    """
    Finds the shortest path between two cells using A*.
    """
    obstacles = []  # Priority queue
    heapq.heappush(obstacles, (0, start))
    wherefrom = {start: None}
    sofar = {start: 0}

    while not len(obstacles) == 0:
        current = heapq.heappop(obstacles)[1]

        if current == goal:
            break
        for next in graph.get_neighborhood(current, moore=False, include_center=False):
            if not pathclear(current, next):
                continue
            new_cost = sofar[current] + 1
            if next not in sofar or new_cost < sofar[next]:
                sofar[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(obstacles, (priority, next))
                wherefrom[next] = current

    path = {}
    current = goal
    while current != start:
        if current in wherefrom:
            prev = wherefrom[current]
            path[prev] = current
            current = prev
        else:
            print("No path found in A* search")
            return {}

    return path

class Car(Agent):
    """
    Agent that moves towards a destination using A*.
    """
    def __init__(self, unique_id, model, spawn, destination=None):
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
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        if road_direction == "Right":
            return dx != -1
        elif road_direction == "Left":
            return dx != 1
        elif road_direction == "Up":
            return dy != -1
        elif road_direction == "Down":
            return dy != 1
        return False

    def find_path(self):
        """
        Finds the path from spawn to destination.
        """
        if self.destination:
            def pathclear(current, next):
                cell_contents = self.model.grid.get_cell_list_contents([next])

                if any(isinstance(agent, Obstacle) for agent in cell_contents):
                    return False

                if any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in cell_contents):
                    roads = [agent for agent in cell_contents if isinstance(agent, Road)]
                    if roads:
                        road = roads[0]
                        return self.is_direction_valid(current, next, road.direction)
                    return True
                return False
            return a_star_search(self.model.grid, self.spawn, self.destination, pathclear)
        return None

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        if self.path and self.pos in self.path:
            next_pos = self.path.get(self.pos)

            if next_pos is not None:
                cell_contents = self.model.grid.get_cell_list_contents([next_pos])

                if not any(isinstance(agent, Car) for agent in cell_contents):
                    traffic_lights = [agent for agent in cell_contents if isinstance(agent, Traffic_Light)]

                    if traffic_lights:
                        traffic_light = traffic_lights[0]
                        if traffic_light.state:
                            self.model.grid.move_agent(self, next_pos)
                            self.direction = self.get_direction(self.pos, next_pos)
                            if next_pos == self.destination:
                                self.model.grid.move_agent(self, next_pos)
                                self.state = "intermediate"
                        else:
                            print(f"Car {self.unique_id} waiting at red traffic light")
                    else:
                        self.model.grid.move_agent(self, next_pos)
                        self.direction = self.get_direction(self.pos, next_pos)
                        if next_pos == self.destination:
                            self.model.grid.move_agent(self, next_pos)
                            self.state = "intermediate"

                else:
                    print(f"Car {self.unique_id} waiting for a clear path")
            else:
                print("No valid next position found.")

    def get_direction(self, current_pos, next_pos):
        """
        Determines the direction the agent should face after moving.
        """
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        if dx == 1:
            return "Right"
        elif dx == -1:
            return "Left"
        elif dy == -1:
            return "Up"
        elif dy == 1:
            return "Down"
        else:
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
            self.model.carInDestination += 1
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state=False, timeToChange=10, type=None):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many steps should the traffic light change color
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
    def __init__(self, unique_id, model, direction="Left"):
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
