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
        
        features['numInvaders'] = len(invaders)

        if (len(invaders) > 0):
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        
        # Scared timer new feature
        sc = myState.getScaredTimer()
        features['foodDist'] = 0
        if sc > 0:
            # print(sc)
            features['numInvaders'] = 0
            if len(invaders) > 0:
                features['invaderDistance'] = -min(dists)
            else:
                features['invaderDistance'] = 0
            if not myState.isPacman():
                features['onDefense'] = -1
            else:
                features['onDefense'] = 1
            fdList = []
            for f in foodList:
                fdList.append(self.getMazeDistance(myPos, f))
            closest = min(fdList)
            features['foodDist'] = closest

        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1

        if (len(enemies) > 0):
            # t = []
            
            track = 0
            for p in enemies:
                if p in invaders:
                    dist = self.getMazeDistance(myPos, p.getPosition()) * 0.9
                    track += dist
                else:
                    dist = self.getMazeDistance(myPos, p.getPosition()) * 0.2
                    track += dist
            features['track'] = track

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -3000,     # -1000
            # we want them dead, not being invaders but in their side of the board
            'onDefense': 1700,         # 100
            # we value that this agent stays in our board (is a pacman)
            'invaderDistance': -500,   # -10
            # invader is 5 pos away f*W = -50
            # invader is 4 pos away f*W = -40
            # -40 >> -50 => we would choose -40 which is right for the defensive agent cause
            # we are choosing to get closest to the invader
            'stop': -900,
            # we always want to keep moving
            'reverse': -1,
            # we don't really want to go back the direction we came
            'track': -1.5,
            # keeps track of both agents, stays close to the middle
            #   'scared': 1,
            'foodDist': -1000     # only for switching to offense
            # two features work together: if scared, forget defence, go for food
        }


class OffensiveReflexAgent(ReflexCaptureAgent):

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

        scared = [a.getScaredTimer() for a in ghosts if a.isScared()]

        if len(scared) > 0:
            features['distanceToGhost'] = 0

        features['eatCapsules'] = len(self.getCapsules(successor))

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 1000,
            'distanceToFood': -10,
            'distanceToGhost': 8,
            'eatCapsules': -15
        }
