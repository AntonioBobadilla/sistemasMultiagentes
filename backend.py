import flask
from flask.json import jsonify
import uuid
import multicity
from multicity import Street, Auto, TrafficLight

games = {}

app = flask.Flask(__name__)

@app.route("/games", methods=["POST"])

def create():
    global games
    id = str(uuid.uuid4())
    games[id] = Street()
    return "ok", 201, {'Location': f"/games/{id}"}

@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    listaAutos = []
    #buscar todos los agentes del modelo y si son cajas o robots incluirlos en el arreglo de diccionarios a mandar al json
    for i in range(len(model.schedule.agents)):
        agent = model.schedule.agents[i]
        print("tipo: ", type(agent))
        print("modelo: ", model.schedule.agents)
        if type(agent) is multicity.Auto:
            listaAutos.append({"x": agent.pos[0], "y": agent.pos[1], "tipo" : "Auto", "horizontal": agent.horizontal})
        if type(agent) is multicity.TrafficLight:
            listaAutos.append({"x": agent.pos[0], "y": agent.pos[1], "tipo" : "TrafficLight", "horizontal": False})
        
        
    return jsonify({"Items":listaAutos})

app.run()