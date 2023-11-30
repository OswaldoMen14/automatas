from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Obstacle, Traffic_Light,Road
import json
import requests

# Size of the board:
number_agents =10
width = 10
height = 10
model = None
currentStep = 0

app = Flask("Traffic example")

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global currentStep, model, number_agents, width, height

    if request.method == 'POST':

        timegenerate = int(request.form.get('timegenerate'))
        file = request.form.get('file')

        model = CityModel(timegenerate, file)

        return jsonify({"message":"Default parameters recieved, model initiated."})


@app.route('/getAgents', methods=['GET'])
def getAgents():
    global model

    if request.method == 'GET':
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 0.05, "z": z, "state": car.state}
                        for x in range(model.grid.width)
                        for z in range(model.grid.height)
                        for car in model.grid.get_cell_list_contents([(x, z)]) if isinstance(car, Car)]

        return jsonify({'positions':carPositions})


@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global model

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(trafficLight.unique_id), "x": x, "y": 0, "z": z, "light": trafficLight.state, "type" : trafficLight.type}
                        for x in range(model.grid.width)
                        for z in range(model.grid.height)
                        for trafficLight in model.grid.get_cell_list_contents([(x, z)]) if isinstance(trafficLight, Traffic_Light)]
        

        return jsonify({'positions':trafficLightPositions})


urlEndpoint = 'http://52.1.3.19:8585/api/attempts'

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, model
    if request.method == 'GET':
        model.step()
        currentStep += 1
        
        if(currentStep % 100 == 0):
            data = {
                "year": "2023",
                "classroom": "301",
                "name": "Equipo1",
                "num_cars": model.carInDestination
            }
            headers = {'Content-type': 'application/json'}

            response = requests.post(urlEndpoint, data=json.dumps(data), headers=headers)
            print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
            print("Response:", response.json())
        
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})






if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)

