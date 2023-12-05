from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.core.directions import Directions

def createTeam(firstIndex, secondIndex, isRed):  # , first, second):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = DefensiveReflexAgent
    secondAgent = OffensiveReflexAgent

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]
    
class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that tries to keep its side Pacman-free.
    This is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = {}

        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        foodList = self.getFood(successor).asList()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0
        
        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        
        # Num of invaders- we want them dead (maxVal = 2)
        features['numInvaders'] = len(invaders)

        # Computes dist to closest invader (maxVal = 1)
        closest = None
        if (len(invaders) > 0):
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = 1 / min(dists)
        
        # keeps track of closest enemy's closest food (maxVal = 1)
        dists = [self.getMazeDistance(myPos, e.getPosition()) for e in enemies]
        i = dists.index(min(dists))
        closest = enemies[i]
        features['distInvFood'] = 0
        if closest is not None:
            enemyFD = [self.getMazeDistance(closest.getPosition(), f) for f in foodList]
            if min(enemyFD) > 0:
                features['distInvFood'] = 1 / min(enemyFD)
            else:
                features['distInvFood'] = 0

        # If opponents eat capsule: ignore invaders and go on offense TODO *** check
        sc = myState.getScaredTimer()
        features['foodDist'] = 0
        if sc > 0:
            # print(sc)
            features['numInvaders'] = 0
            features['invaderDistance'] = -min(dists)
            if not myState.isPacman():
                features['onDefense'] = -1
            else:
                features['onDefense'] = 1
            fdList = []
            for f in foodList:
                fdList.append(self.getMazeDistance(myPos, f))
            closest = min(fdList)
            features['foodDist'] = closest

        # indicator function: True if next move is STOP
        if (action == Directions.STOP):
            features['stop'] = 1
        
        # indicator function: True if nex move is in the opposite direction
        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1


        # will try to track both opponents, giving a stronger weight to invaders
        # TODO: on some occations will get stuck and move into the wall
        # sometimes goes on offence if weights are too high
        # maxVal = 2
        if(len(enemies) > 0):
            # t = []
            
            track = 0
            for p in enemies:
                dist = self.getMazeDistance(myPos, p.getPosition()) 
                if dist == 0:
                    continue
                if p in invaders:
                    track += 1 / dist 
                else:
                    dist *=  0.5
                    track += 1 / dist
            features['track'] = track

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -100,       # we want them dead, or on their side of the board  
            'onDefense': 40,          # we value that this agent stays in our board (is a pacman)  
            'invaderDistance': 90, 
            'stop': -100,               # we always want to keep moving  
            'reverse': -1,              # we don't really want to go back the direction we came  
            'track': 20,              # keeps track of both agents, stays close to the middle  
            'foodDist': -1000,          # only for switching to offense
            'distInvFood': -25         # two features work together: if scared, go for food  
        }

class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food.
    This agent will give you an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        # Compute distance to the nearest food.
        foodList = self.getFood(successor).asList()

        # This should always be True, but better safe than sorry.
        if (len(foodList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghosts = [a for a in enemies if not a.isPacman() and a.getPosition() is not None]

        if (len(ghosts) > 0):
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
            features['distanceToGhost'] = min(dists)

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 1000,
            'distanceToFood': -10,
            'distanceToGhost': 7
        }

