from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Obstacle, Traffic_Light,Road

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
        currentStep = 0

        model = CityModel(5)

        return jsonify({"message":"Default parameters recieved, model initiated."})


@app.route('/getAgents', methods=['GET'])
def getAgents():
    global model

    if request.method == 'GET':
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 1, "z": z, "state": car.state}
                        for x in range(model.grid.width)
                        for z in range(model.grid.height)
                        for car in model.grid.get_cell_list_contents([(x, z)]) if isinstance(car, Car)]

        return jsonify({'positions':carPositions})


@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global model

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(trafficLight.unique_id), "x": x, "y": 1, "z": z, "light": trafficLight.state}
                        for x in range(model.grid.width)
                        for z in range(model.grid.height)
                        for trafficLight in model.grid.get_cell_list_contents([(x, z)]) if isinstance(trafficLight, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})



@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, model
    if request.method == 'GET':
        model.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)

