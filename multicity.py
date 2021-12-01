from mesa import Agent, Model
from mesa.space import Grid
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from numpy import true_divide
from pathfinding.core.diagonal_movement import DiagonalMovement

class Auto(Agent):
  def __init__(self, model, pos, lane):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "automobile"
    self.index = 0
    self.horizontal = False
    self.direction = 1 #
    self.assignDirection()
    self.lane = lane 
    self.passedLight = False



  def checkNeighbors(self, neighborList, type):
    for neighbor in neighborList:
        if neighbor.type == type:
          return type
    return ""

  def getNeighbor(self, neighborList, type):
    for neighbor in neighborList:
        if neighbor.type == type:
          return neighbor
    return ""
  
  def assignDirection(self):
    #Si la casilla a la izquierda esta fuera de la matriz
    if self.pos[0] - 1 < 0 and self.pos[0] + 1 < len(self.model.matrix):
      neighborList = self.model.grid[self.pos[0] + 1][self.pos[1]]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          self.horizontal = True
          self.direction = 1
    #Si la casilla de abajo esta fuera de la matriz
    elif self.pos[1] - 1 < 0 and self.pos[1] + 1 < len(self.model.matrix[0]):
      neighborList = self.model.grid[self.pos[0]][self.pos[1] + 1]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          self.horizontal = False
          self.direction = 1
    #Si la casilla derecha esta fuera de la matriz
    elif self.pos[0] - 1 >= 0 and self.pos[0] + 1 >= len(self.model.matrix):
      neighborList = self.model.grid[self.pos[0] -1][self.pos[1]]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          self.horizontal = True
          self.direction = -1
    #Si la casilla de arriba esta fuera de la matriz
    elif self.pos[1] - 1 >= 0 and self.pos[1] + 1 >= len(self.model.matrix[0]):
      neighborList =  self.model.grid[self.pos[0]][self.pos[1] - 1]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          self.horizontal = False
          self.direction = -1
    #Si la casilla se encuentra dentro del rango
    else:
      leftAndRight = False
      neighborList =  self.model.grid[self.pos[0] - 1][self.pos[1]]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          leftAndRight = True
      
      neighborList = self.model.grid[self.pos[0] + 1][self.pos[1]]
      if self.checkNeighbors(neighborList, "normalBlock") == "normalBlock":
          leftAndRight = True
      
      if leftAndRight:
        self.horizontal = False
        self.direction = -1
      else:
        self.horizontal = False
        self.direction = -1
    
    print("HORIZONTAL = ", self.horizontal)
    print("DIRECTION = ", self.direction)
      

  def step(self):
    # print("hola")
    if self.lane:
      blockType = "normalBlockLeft"
    else:
      blockType  = "normalBlock"
    move = False
    if self.horizontal:
      # verifica que no se salga del grid y que puede seguir avanzando en horizontal (X)
      if self.pos[0] + self.direction <= self.model.columns:
        #Se verifica si al que se va a avanzar tambien tiene un normalblock como next move
        neighborList = self.model.grid[self.pos[0] + self.direction][self.pos[1]]
        #checar si es un bloque normal, un semaforo o un coche
        if self.checkNeighbors(neighborList, blockType) == blockType or self.checkNeighbors(neighborList, "trafficLightGreen") == "trafficLightGreen" or self.checkNeighbors(neighborList, "trafficLightRed") == "trafficLightRed" or self.checkNeighbors(neighborList, "automobile") == "automobile" or self.checkNeighbors(neighborList, "normalBlockBoth") == "normalBlockBoth":
          #Si se cumplen estas condiciones, avanza al siguiente normalBlock
          if self.checkNeighbors(neighborList, blockType) == blockType or self.checkNeighbors(neighborList, "normalBlockBoth") == "normalBlockBoth":
            nextmove = (self.pos[0] + self.direction, self.pos[1])
            move = True
          #Si encuentra un traffic Light, verifica su estado y decide si puede avanzar o no 
          elif self.checkNeighbors(neighborList, "trafficLightGreen") == "trafficLightGreen":
            print("TRAFFIC LIGHT GREEN")
            trafficLight = self.getNeighbor(neighborList,"trafficLightGreen")
            if trafficLight.green and trafficLight.timer >= 4 and self.passedLight == False:
              nextmove = (self.pos[0] + self.direction, self.pos[1])
              move = True
          if self.checkNeighbors(neighborList, "automobile") == "automobile":
            move = False
          #Ignora el estado del siguiente semaforo ya que siempre se encontrará en rojo 
        else:
          #Significa que ya no hay camino en horizontal y ahora comenzará el movimiento en vertical 
          self.horizontal = False
          # checa si la posición + 1 es accesible 
          if self.pos[1] + 1 >= self.model.rows:
            self.direction = -1
          elif self.pos[1] - 1 < 0:
            self.direction = 1
          elif self.pos[1] + 1 < self.model.rows:
            neighborList = self.model.grid[self.pos[0]][self.pos[1] + 1]
            if self.checkNeighbors(neighborList, blockType) == blockType:
              self.direction = 1
            else:
              self.direction = -1
    else:
      if self.pos[1] + self.direction <= self.model.columns:
        #Se verifica si al que se va a avanzar tambien tiene un normalblock como next move (Y)
        neighborList = self.model.grid[self.pos[0]][self.pos[1] + self.direction]
        #checar si es un bloque normal, un semaforo o un coche
        if self.checkNeighbors(neighborList, blockType) == blockType or self.checkNeighbors(neighborList, "trafficLightGreen") == "trafficLightGreen" or self.checkNeighbors(neighborList, "trafficLightRed") == "trafficLightRed" or self.checkNeighbors(neighborList, "automobile") == "automobile" or self.checkNeighbors(neighborList, "normalBlockBoth") == "normalBlockBoth":
          #Si se cumplen estas condiciones, avanza al siguiente normalBlock
          if self.checkNeighbors(neighborList, blockType) == blockType or self.checkNeighbors(neighborList, "normalBlockBoth") == "normalBlockBoth":
            nextmove = (self.pos[0], self.pos[1] + self.direction)
            move = True
          #Si encuentra un traffic Light, verifica su estado y decide si puede avanzar o no 
          elif self.checkNeighbors(neighborList, "trafficLightGreen") == "trafficLightGreen":
            trafficLight = self.getNeighbor(neighborList,"trafficLightGreen")
            if trafficLight.green and trafficLight.timer >= 4 and self.passedLight == False:
              nextmove = (self.pos[0], self.pos[1] + self.direction)
              move = True
          if self.checkNeighbors(neighborList, "automobile") == "automobile":
            move = False
        else:
          #Significa que ya no hay camino en vertical y ahora comenzará el movimiento en horizontal (X)
          self.horizontal = True
          # checa si la posición + 1 en x se encuentra dentro de la matriz
          if self.pos[0] + 1 >= self.model.columns:
            self.direction = -1
          # checa si la posición - 1 en x se encuentra dentro de la matriz
          elif self.pos[0] - 1 < 0:
            self.direction = 1
          #checa si la posicion de arriba esta bloqueada
          elif self.pos[0] + 1 < self.model.columns:
            neighborList = self.model.grid[self.pos[0] + 1][self.pos[1]]
            if self.checkNeighbors(neighborList, blockType) == blockType:
              self.direction = 1
            else:
              self.direction = -1
    if move:
      self.model.grid.move_agent(self, nextmove)


class StreetBlock(Agent):
  def __init__(self, model, pos, type):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = type

class TrafficLight(Agent):
  def __init__(self, model, pos, type, activated):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = type
    self.green = False
    self.activated = activated
    self.timer = 0

  #Se define el tiempo que tardara el semaforo con luz roja y con luz verde
  def step(self):
    if self.activated:
      self.timer += 1
      print("active ", self.model.trafficLightActive)
      self.type = "trafficLightGreen"
      self.green = True
    else:
      self.type = "trafficLightRed"
      self.green = False
    # su el tiempo (timer) del semaforo llego a su límite, se reinician los valores
    if self.timer > 9 and self.activated:
      self.green = False
      self.activated = False
      self.timer = 0
      self.model.trafficLightActive += 1
      self.type = "trafficLightRed"
      # si se llego al ultimo semaforo, se reinicia el ciclo y se enciende el primero
      if self.model.trafficLightActive >= len(self.model.trafficLights):
        self.model.trafficLightActive = 0
      self.model.trafficLights[self.model.trafficLightActive].activated = True
      self.model.trafficLights[self.model.trafficLightActive].type = "trafficLightGreen"
      self.model.trafficLights[self.model.trafficLightActive].timer = 0
    if self.timer > 9:
      self.timer = 0
      
        



# definir tipo de coche dependiendo su carril, izquierdo o derecho
# si es izquierdo siempre tiene que checar si tiene un uno a la izquierda y arriba
class Street(Model):
  def __init__(self):
    super().__init__()
    self.schedule = RandomActivation(self)
    self.grid = MultiGrid(67, 68, torus=False)
    self.trafficLights = []
    self.trafficLightActive = 0
    self.matrix = [ 
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,0],
	[0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,0],
	[0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,4,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]
    self.rows = len(self.matrix)
    self.columns = len(self.matrix[0])
    self.placeBlocks()
    # auto = Auto(self,(2,65),False)
    # self.grid.place_agent(auto, auto.pos)
    # self.schedule.add(auto)
    # auto = Auto(self,(2,63),False)
    # self.grid.place_agent(auto, auto.pos)
    # self.schedule.add(auto)
    # auto = Auto(self,(2,61),False)
    # self.grid.place_agent(auto, auto.pos)
    # self.schedule.add(auto)
    # auto = Auto(self,(0,0),False)
    # self.grid.place_agent(auto, auto.pos)
    # self.schedule.add(auto)

    for x in range(1,3):
      if x % 2 == 0: #Gray
        automobile = Auto(self, (x, self.columns-x),False)
        self.grid.place_agent(automobile, automobile.pos)
        self.schedule.add(automobile)

      else: #Yellow
        automobile = Auto(self, (x, self.columns-x),True)
        self.grid.place_agent(automobile, automobile.pos)
        self.schedule.add(automobile)


  def step(self):
    self.schedule.step()
  
  def placeBlocks(self):
    first = True
    for _,x,y in self.grid.coord_iter():
      if self.matrix[y][x] == 1:
        block = StreetBlock(self,(x,y), "normalBlock")
        self.grid.place_agent(block, block.pos)
      elif self.matrix[y][x] == 0:
        block = StreetBlock(self,(x,y), "blockedBlock")
        self.grid.place_agent(block, block.pos)
      elif self.matrix[y][x] == 2:
        if first:
          print("FIRST", first)
          block = TrafficLight(self,(x,y), "trafficLightGreen", True)
          first = False
        else:
          block = TrafficLight(self,(x,y), "trafficLightRed", False)
        self.trafficLights.append(block)
        self.grid.place_agent(block, block.pos)
        self.schedule.add(block)
      elif self.matrix[y][x] == 3:
        block = StreetBlock(self,(x,y), "normalBlockLeft")
        self.grid.place_agent(block, block.pos)
      elif self.matrix[y][x] == 4:
        block = StreetBlock(self,(x,y), "normalBlockBoth")
        self.grid.place_agent(block, block.pos)

  


def agent_portrayal(agent):
  if(agent.type == "automobile"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Blue", "Layer": 1}
  elif (agent.type == "normalBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Gray", "Layer": 0}
  elif (agent.type == "normalBlockLeft"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Yellow", "Layer": 0}
  elif (agent.type == "normalBlockBoth"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Purple", "Layer": 0}
  elif (agent.type == "blockedBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Black", "Layer": 0}
  elif (agent.type == "trafficLightGreen"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Green", "Layer": 0}
  elif (agent.type == "trafficLightRed"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Red", "Layer": 0}

grid = CanvasGrid(agent_portrayal, 67, 68, 450, 450)

# server = ModularServer(Street, [grid], "Multicity", {})
# server.port = 8521
# server.launch()