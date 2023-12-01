from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer
import json
import requests

"""

Code made by Alan Hernández and Oswaldo Mendizábal
30/11/2023

"""

def agent_portrayal(agent):
    """
    Define how agents are portrayed in the visualization.

    Args:
        agent: The agent to be portrayed.

    Returns:
        dict: A dictionary specifying the agent's portrayal properties.
    """
    if agent is None:
        return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if isinstance(agent, Car):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1

    if isinstance(agent, Road):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0

    if isinstance(agent, Destination):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if isinstance(agent, Car):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1

    if isinstance(agent, Traffic_Light):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if isinstance(agent, Obstacle):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    return portrayal

# Read the width and height of the grid from a map file
width = 0
height = 0

with open('static/city_files/2022_base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

# Define model parameters
model_params = {"N": 2, "file": 'static/city_files/2023_base.txt'}

# Create a CanvasGrid for visualization
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# Create a ModularServer for the CityModel
server = ModularServer(CityModel, [grid], "Traffic Base", model_params)

# Set the port for the server
server.port = 8521  # The default

# Launch the server
server.launch()
