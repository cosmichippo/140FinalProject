from pacai.agents.capture.reflex import ReflexCaptureAgent

def createTeam(firstIndex, secondIndex, isRed, first, second):
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

        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
        # we want them dead, not being invaders but in their side of the board
            'onDefense': 100,
        # we value that this agent stays in our board (is a pacman)
            'invaderDistance': -10,
        # invader is 5 pos away f*W = -50
        # invader is 4 pos away f*W = -40
        # -40 >> -50 => we would choose -40 which is right for the defensive agent cause we are choosing to get closest to the invader
            'stop': -100,
        # we always want to keep moving
            'reverse': -2
        # we don't really want to go back the direction we came
        }
    

# 1. Stay on our side of the border as close to the opponents as possible without tresspassing
# 2. Only tresspass if distance to closest opponent is greater than x to get a food very quickly


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

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 100,
            # eating food
            'distanceToFood': -1
            # minimizing the distance to food
        }

#  if a ghost comes near us (certain radious) go get a capsule or run away