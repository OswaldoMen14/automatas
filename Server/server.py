from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Obstacle, Traffic_Light, Road
import json
import requests

"""

Code made by Alan Hernández and Oswaldo Mendizábal
30/11/2023

"""

# Size of the board:
number_agents = 10
width = 10
height = 10
model = None
currentStep = 0

# Create a Flask application
app = Flask("Traffic example")

# Route to initialize the model
@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global currentStep, model, number_agents, width, height

    if request.method == 'POST':
        # Retrieve parameters from the request
        timegenerate = int(request.form.get('timegenerate'))
        file = request.form.get('file')

        # Initialize the CityModel with provided parameters
        model = CityModel(timegenerate, file)

        return jsonify({"message": "Default parameters received, model initiated."})

# Route to get positions of car agents
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global model

    if request.method == 'GET':
        # Get positions of car agents in the model
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 0.05, "z": z, "state": car.state}
                        for x in range(model.grid.width)
                        for z in range(model.grid.height)
                        for car in model.grid.get_cell_list_contents([(x, z)]) if isinstance(car, Car)]

        return jsonify({'positions': carPositions})

# Route to get positions of traffic light agents
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global model

    if request.method == 'GET':
        # Get positions of traffic light agents in the model
        trafficLightPositions = [{"id": str(trafficLight.unique_id), "x": x, "y": 0, "z": z, "light": trafficLight.state,
                                  "type": trafficLight.type}
                                 for x in range(model.grid.width)
                                 for z in range(model.grid.height)
                                 for trafficLight in model.grid.get_cell_list_contents([(x, z)]) if
                                 isinstance(trafficLight, Traffic_Light)]

        return jsonify({'positions': trafficLightPositions})

# Define an external endpoint for data submission
urlEndpoint = 'http://52.1.3.19:8585/api/attempts'

# Route to update the model
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, model
    if request.method == 'GET':
        # Perform a step in the model simulation
        model.step()
        currentStep += 1
        print("Step:", currentStep)

        # Every 100 steps, submit data to an external endpoint
        if currentStep % 100 == 0:
            data = {
                "year": "2023",
                "classroom": "301",
                "name": "Equipo1 arbolitos ramificado AO",
                "num_cars": model.carInDestination
            }

            print("Car in the destination:", str(model.carInDestination))
            headers = {'Content-type': 'application/json'}

            # Submit data to the external endpoint
            response = requests.post(urlEndpoint, data=json.dumps(data), headers=headers)
            print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
            print("Response:", response.json())

        return jsonify({'message': f'Model updated to step {currentStep}.', 'currentStep': currentStep})

# Run the Flask application
if __name__ == '__main__':
    app.run(host="localhost", port=8585, debug=True)
