# Defensive agent for second check
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

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0
        
        """
        if (myState.getScaredTimer() > 0):
            print(myState.getScaredTimer)
            features['numInvaders'] = 0
            features['invaderDistance'] = -0.001
            fdList = []
            for f in foodList:
                fdList.append(self.getMazeDistance(myPos, f))
            closest = min(fdList)
        """

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

        # will try to track both opponents, giving a stronger weight to invaders
        # TODO: on some occations will get stuck and move into the wall
        # sometimes goes on offence if weights are too high

        if (len(enemies) > 0):
            # t = []
            track = 0
            for p in enemies:
                if p in invaders:
                    dist = self.getMazeDistance(myPos, p.getPosition()) * 0.9
                    track += dist
                else:
                    dist = self.getMazeDistance(myPos, p.getPosition()) * 0.5
                    track += dist
            features['track'] = track

            """
            for p in enemies:
                if p in invaders:
                    t.append(self.getMazeDistance(myPos, p.getPosition()))
                else:
                    t.append(self.getMazeDistance(myPos, p.getPosition()))
            features['track'] = (max(t) ** 2) - (min(t) ** 2)
            """
        # TODO: add scared time check to go on offence: set onDefence = 0?
        # TODO: idea for offence
        #  noticed that it could be helpful for our agent to get a quick kill
        #  on a pacman when respawning if its within a certain radius

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -3000,     # -1000
            # we want them dead, not being invaders but in their side of the board
            'onDefense': 1000,         # 100
            # we value that this agent stays in our board (is a pacman)
            'invaderDistance': -500,   # -10
            # invader is 5 pos away f*W = -50
            # invader is 4 pos away f*W = -40
            'stop': -900,
            # we always want to keep moving
            'reverse': -1,
            # we don't really want to go back the direction we came
            'track': -1.5,
            # keeps track of both agents, stays close to the middle
            # 'scared': 1,
            #   'foodDist': 1
            # two features work together: if scared, forget defence, go for food
        }

    """
    def isInRadius(self, myPos, enemies, radius):
        # return bool weather enemy in specified radius
        return b
    def foodInRadius(self, myPos, foodList, radius):
        # return true if food in specified radius
        return b
    """
    
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
