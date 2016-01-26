import math, random
class Planet:
  def __init__(self, x, y, alignment, population):
    self.x, self.y = x, y
    self.alignment = alignment
    self.population = population

  def proliferate(self):
    self.population += 1

  def dividePopulation(self):
    old_population = self.population
    self.population = int(math.ceil(self.population/2))
    return old_population-self.population;

  def intakePopulation(self, in_alignment, num):
    if in_alignment != self.alignment:
      if num >= self.population:
        self.population = num-self.population
        self.alignment = in_alignment
      else: self.population -= num
    else:
      self.population += num

class Transfer:
  def __init__(self, a, b, apos, bpos, value, alignment):
    self.a, self.b = a, b
    self.apos = apos[:]
    self.bpos = bpos
    self.pos = apos[:]
    self.value = value
    self.alignment = alignment

  def increment(self):
    """Returns true if transaction is complete"""
    c = 0.2
    if self.bpos[0] == self.apos[0]:
      if self.apos[1] > self.bpos[1]:
        self.pos[1] -= c
      else:
        self.pos[1] += c
    else:
      m = abs(float(self.apos[1]-self.bpos[1])/(self.apos[0]-self.bpos[0]))
      dx = math.sqrt((c*c)/(1+m*m))
      dy = m*dx
      if self.apos[0] < self.bpos[0]:
        self.pos[0] += dx
      else: self.pos[0] -= dx
      if self.apos[1] < self.bpos[1]:
        self.pos[1] += dy
      else: self.pos[1] -= dy
    distance = math.sqrt(math.pow(self.pos[0]-self.bpos[0], 2)+
                         math.pow(self.pos[1]-self.bpos[1], 2))
    if distance < 10:
      return True
    return False

class AI:
  def __init__(self, decision_func, name, alignment):
    self.decision = decision_func
    self.name = name
    self.alignment = alignment

class Game:
  def __init__(self, ai_list):
    #generate planets
    self.planets = []
    self.ais = ai_list
    for ai in self.ais:
      #three planets per ai
      for i in range(0, 3):
        #make sure the planets aren't too close together
        too_close = True
        xpos, ypos = 0, 0
        while too_close:
          #we add padding (50)
          xpos = random.randint(50, 590)
          ypos = random.randint(50, 430)
          too_close = False
          for i in self.planets:
            distance = math.sqrt(math.pow(xpos-i.x, 2)+math.pow(ypos-i.y, 2))
            if distance < 100:
              too_close = True
              break
        print([xpos, ypos])
        self.planets.append(Planet(xpos, ypos, ai.alignment, 50))
    self.transfers = [];

  def AITurns(self):
    new_transfers = []
    #get new transfers from the ai's decision function
    for i in self.ais:
      new_transfers.append((i.decision(self.planets[:], i.alignment), i,))
    #add the new transfers to the game
    for transfer in new_transfers:
      for move in transfer[0]:
        #ensures that an ai can't make moves for an enemy
        if self.planets[move[0]].alignment == transfer[1].alignment:
          self.startTransfer(move[0], move[1])

  def startTransfer(self, a, b):
    value = self.planets[a].dividePopulation()
    alignment = self.planets[a].alignment
    apos = [self.planets[a].x, self.planets[a].y]
    bpos = [self.planets[b].x, self.planets[b].y]
    self.transfers.append(Transfer(a, b, apos, bpos, value, alignment))

  def incrementTransfers(self):
    kept_transfers = []
    for i in range(0, len(self.transfers)):
      if not self.transfers[i].increment():
        kept_transfers.append(self.transfers[i])
      else:
        transfer = self.transfers[i]
        self.planets[transfer.b].intakePopulation(transfer.alignment,
                                                  transfer.value)
    self.transfers = kept_transfers

  def proliferatePlanets(self):
    for i in range(0, len(self.planets)):
      if self.planets[i].alignment != 'gray':
        self.planets[i].proliferate()
