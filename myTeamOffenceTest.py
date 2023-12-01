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
        
        # Scared timer new feature
        sc = myState.getScaredTimer()
        features['foodDist'] = 0
        if sc > 0:
            print(sc)
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


        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1

        # will try to track both opponents, giving a stronger weight to invaders
        # TODO: on some occations will get stuck and move into the wall
        # sometimes goes on offence if weights are too high

        if(len(enemies) > 0):
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

            """
            for p in enemies:
                if p in invaders:
                    t.append(self.getMazeDistance(myPos, p.getPosition()))
                else:
                    t.append(self.getMazeDistance(myPos, p.getPosition()))
            features['track'] = (max(t) ** 2) - (min(t) ** 2)
            """
            


        # TODO: add scared time check to go on offence: set onDefence = 0?


        ### TODO: idea for offence
        ###  noticed that it could be helpful for our agent to get a quick kill
        ###  on a pacman when respawning if its within a certain radius

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
        # -40 >> -50 => we would choose -40 which is right for the defensive agent cause we are choosing to get closest to the invader
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
    # prioritize furthest food
    # prioritize capsules
    # radius to run away

    def __init__(self, index, **kwargs):
        super().__init__(index)


    def getFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        # current = self.getAgentState(self.index)
        features['successorScore'] = self.getScore(successor)

        # Compute distance to the nearest food.
        foodList = self.getFood(successor).asList()

        # Check for capsules within the radius
        capsules = self.getCapsules(successor)

        # This should always be True, but better safe than sorry.
        
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            maxDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = maxDistance

        # if len(capsules) > 0:
        #     closestCap = min([self.getMazeDistance(myPos, cap) for cap in capsules])
        #     features['capsulesInRadius'] = closestCap
        
        if action == Directions.STOP:
            features['stop'] = 2
        
        rev = Directions.REVERSE[successor.getAgentState(self.index).getDirection()]
        if action == rev:
            features['reverse'] = 2
        
        # List of ghost indices
        ghostList = self.getOpponents(successor)
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        scared = [a.getScaredTimer() for a in enemies if not a.isPacman() and a.isScared()]


        # Closest ghost


        """
        if len(ghostList) > 0:
            ghostPos = gameState.getAgentState(ghostList[0]).getPosition()
            ghostDistance = self.getMazeDistance(myPos, ghostPos)
            # Distance to closest ghost
            features['distanceToGhost'] = ghostDistance
        # Radius to check if the ghost is within

        """
        if len(ghostList) > 0:
            ghostPos = [successor.getAgentState(i) for i in ghostList]
            invaders = [a for a in ghostPos if  a.getPosition() is not None]
            ghostDistance = [self.getMazeDistance(myPos, x.getPosition()) for x in invaders]
            # Distance to closest ghost
            features['distanceToGhost'] = min(ghostDistance)   #TODO: distToG is being overwritten in lines 209 & 216
            ghostDistance = min(ghostDistance)
        

        radius = 5
        # If ghost is in the radius
        if (myState.isPacman()):
            features['onOffense'] = 1
            if (ghostDistance <= radius):
                features['distanceToGhost'] = ghostDistance   # 100
                features['capsulesInRadius'] = 1 if any(self.getMazeDistance(myPos, cap) <= radius for cap in capsules) else 0  #TODO: use capsule dist for this
            else:
                features['reverse'] = 0
        else:
            features['onOffense'] = -0.5        #TODO: reevaluate this line
            if (ghostDistance <= radius):
                features['distanceToGhost'] = -1 * ghostDistance
            else:
                features['reverse'] = 0

        if len(scared) > 0:
            print(scared)
            features['distanceToGhost'] = 0
            features['distanceToFood'] = features['distanceToFood'] * 2

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 1000,  # 100
            'distanceToFood': -100,  # -10
            'reverse': -2,           
            'stop': -100,
            'onOffense': 100,
            'distanceToGhost': -90,  # -10             # Weight for distance to ghost
            'capsulesInRadius': 50    # Weight for capsules within radius
        }
