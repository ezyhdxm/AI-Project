# myAgentP3.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
# This file was based on the starter code for student bots, and refined 
# by Mesut (Xiaocheng) Yang


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint
from game import Actions
#########
# Agent #
#########
class MyAgent(CaptureAgent):
  """
  A Q-learning agent.
  """
  directionsAsList = [('West', (-1, 0)), ('East', (1, 0)), ('North', (0, 1)), ('South', (0, -1))]
  flag = 0
  weights = [1,1,1,1,0]
  discount = 0.8
  alpha = 0.2
  history = None
  time = 600
  expended = set()

  def getLegalNeighbors(self, position, walls):
    x,y = position
    x_int, y_int = int(x + 0.5), int(y + 0.5)
    neighbors = []
    for dir, vec in self.directionsAsList:
      dx, dy = vec
      next_x = x_int + dx
      if next_x < 0 or next_x == walls.width: continue
      next_y = y_int + dy
      if next_y < 0 or next_y == walls.height: continue
      if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
    return neighbors

  def getFeatures(self, state, action):

    foods = state.getFood().asList()
    ghosts = [state.getAgentPosition(ghost) for ghost in state.getGhostTeamIndices()]
    friends = [state.getAgentPosition(pacman) for pacman in state.getPacmanTeamIndices() if pacman != self.index]
    walls = state.getWalls()
    
    

    pacman = state.getAgentPosition(self.index)
    x, y = pacman
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)
    nextPac = next_x, next_y

    closestFood = min(self.distancer.getDistance(nextPac, food) for food in foods) + 2.0 \
      if len(foods) > 0 else 1.0
    closestGhost = min(self.distancer.getDistance(nextPac, ghost) for ghost in ghosts) + 1.0 \
      if len(ghosts) > 0 else 1.0
    closestFriend = min(self.distancer.getDistance(nextPac, friend) for friend in friends) + 1.0 \
      if len(friends) > 0 else 1.0
    
    neighbors = self.getLegalNeighbors(nextPac,walls)
    
    isCornered = 1
    #isCornered = len(neighbors) + closestGhost
    closestFoodReward = 1.0 / closestFood
    closestGhostPenalty = -2.0**(2.0/(closestGhost)) + 1.0 if closestGhost <= 8 else 0
    closestFriendPenalty = -1.0 / (closestFriend ** 2) if closestFriend <= 5 else 0

    numFood = len(foods)

    features = [numFood, closestFoodReward, closestGhostPenalty, closestFriendPenalty, isCornered]

    return features

  def evaluationFunction(self, state, action):

    features = self.getFeatures(state, action)

    value = sum(feature * weight for feature, weight in zip(features, self.weights))
    return value
  
  
  
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    # Make sure you do not delete the following line. 
    # If you would like to use Manhattan distances instead 
    # of maze distances in order to save on initialization 
    # time, please take a look at:
    # CaptureAgent.registerInitialState in captureAgents.py.
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)

  def getReward(self, state):
    
    pacman = state.getAgentPosition(self.index)
    reward = 0

    if pacman == (1, 1):
      if self.flag == 0:
        self.flag += 1
        reward -= 1
      else:
        reward -= 5
    elif self.history == None:
      reward -= 1
    else:
      dFood = self.history[0] - self.getNumFood(state)
      if self.getNumFood(state) == 2:
        reward += 100

      if self.time < 1:
        reward -= 100

      if dFood > 0:
        reward += 1
      else:
        reward -= 1
      
      return reward

  def update(self, state, action, nextState):

    reward = self.getReward(nextState)
    legalActions = nextState.getLegalActions(self.index)
    filteredActions = actionsWithoutReverse(actionsWithoutStop(legalActions), nextState, self.index)
    if len(filteredActions)==0:
      qvalue = 0.0
    else: 
      nextQsa = []
      for nextAction in filteredActions:
        q = self.evaluationFunction(nextState, nextAction)
        nextQsa.append(q)
      qvalue = max(nextQsa)
    
    diff = reward + self.discount * qvalue - self.evaluationFunction(state,action)
    multi = float(self.alpha * diff)
    features=self.getFeatures(state, action)
    
    for i in range(len(features)):
      self.weights[i] += features[i] * multi
    
    return 

  def getNumFood(self, state):
    
    foods = state.getFood().asList()
    numFood = len(foods)
    return numFood 

  def chooseAction(self, gameState):

    """
    Picks among actions randomly.
    """
    teammateActions = self.receivedBroadcast
    # Process your teammate's broadcast! 
    # Use it to pick a better action for yourself

    pacman = gameState.getAgentPosition(self.index)
    self.expended.add(pacman)

    actions = gameState.getLegalActions(self.index)
    filteredActions = actionsWithoutReverse(actionsWithoutStop(actions), gameState, self.index)
    currentAction = random.choice(actions) # Change this!

    numFood = self.getNumFood(gameState)

    if self.history != None:
      food, preState, action = self.history
      self.update(preState, action, gameState)
      print(self.weights)

    val = float('-inf')
    best = None

    for action in filteredActions:
      #new_state = gameState.generateSuccessor(self.index, action)
      new_state_val = self.evaluationFunction(gameState, action)
      if new_state_val > val:
        val = new_state_val
        best = action
    
    self.time -= 1
    self.history = (numFood, gameState, best)
    if best == None:
      return currentAction
    return best            

def actionsWithoutStop(legalActions):
  """
  Filters actions by removing the STOP action
  """
  legalActions = list(legalActions)
  if Directions.STOP in legalActions:
    legalActions.remove(Directions.STOP)
  return legalActions

def actionsWithoutReverse(legalActions, gameState, agentIndex):
  """
  Filters actions by removing REVERSE, i.e. the opposite action to the previous one
  """
  legalActions = list(legalActions)
  reverse = Directions.REVERSE[gameState.getAgentState(agentIndex).configuration.direction]
  if len (legalActions) > 1 and reverse in legalActions:
    legalActions.remove(reverse)
  return legalActions
