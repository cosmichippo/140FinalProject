from pacai.agents.learning.reinforcement import ReinforcementAgent
from pacai.util import reflection
from random import random, choice
from pacai.core.featureExtractors import FeatureExtractor 
from pacai.core.directions import Directions
from pacai.student.reinforcementCaptureAgent import ReinforcementCaptureAgent
from pacai.util import util
from pacai.core.distance import manhattan

class QLearningAgent(ReinforcementCaptureAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)
        print(kwargs)

        # You can initialize Q-values here.
        self.qValues = dict()

    def getQValue(self, state, action):
        """
        Get the Q-Value for a `pacai.core.gamestate.AbstractGameState`
        and `pacai.core.directions.Directions`.
        Should return 0.0 if the (state, action) pair has never been seen.
        """
        return self.qValues.get((state, action), 0.0)

    def getValue(self, state):
        """
        Return the value of the best action in a state.
        I.E., the value of the action that solves: `max_action Q(state, action)`.
        Where the max is over legal actions.
        Note that if there are no legal actions, which is the case at the terminal state,
        you should return a value of 0.0.

        This method pairs with `QLearningAgent.getPolicy`,
        which returns the actual best action.
        Whereas this method returns the value of the best action.
        """
        action = self.getPolicy(state)
        # print(action)
        if action is not None:
            return self.getQValue(state, action)
        return 0.0

    def getPolicy(self, state):
        """
        Return the best action in a state.
        I.E., the action that solves: `max_action Q(state, action)`.
        Where the max is over legal actions.
        Note that if there are no legal actions, which is the case at the terminal state,
        you should return a value of None.

        This method pairs with `QLearningAgent.getValue`,
        which returns the value of the best action.
        Whereas this method returns the best action itself.
        """
        state_action_pairs = [(state, action) for action in state.getLegalActions(self.index)]
        if len(state_action_pairs):
            # print(state_action_pairs)
            # print(state_action_pairs)
            maxPair = max(state_action_pairs, key = lambda x: self.getQValue(x[0], x[1]))
            return maxPair[1]
        return None

    def update(self, state, action, nextState, reward):
        sample = reward + (self.getGamma() * self.getValue(nextState))
        qVal = (1 - self.getAlpha()) * self.getQValue(state, action)
        qVal += self.getAlpha() * sample
        self.qValues[(state, action)] = qVal
        # print(self.qValues)

    def getAction(self, state):
        actions = state.getLegalActions(self.index)
        bestAction = self.getPolicy(state)
        rand = random()
        
        if rand < self.getEpsilon():
            return choice(actions)
        return bestAction


class CaptureQAgent(QLearningAgent): 
    def __init__(self, index, epsilon = 0.05, gamma = 0.8, alpha = 0.02, numTraining = 0, **kwargs):
        kwargs['epsilon'] = epsilon
        kwargs['gamma'] = gamma
        kwargs['alpha'] = alpha
        kwargs['numTraining'] = numTraining

        super().__init__(index, **kwargs)

    def getAction(self, state):
        """
        Simply calls the super getAction method and then informs the parent of an action for Pacman.
        Do not change or remove this method.
        """
        action = super().getAction(state)
        self.doAction(state, action)  # logs the past (state, action) pair
        return action

#IMPORT THIS ONE

class CaptureApproximateQAgent(CaptureQAgent):

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)
        self.weights = {
            'numInvaders': -1000,
            'onDefense': 100,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2
        }
        print("INIT WEIGHTS", self.weights)
        self.featExtractor = DefensiveFeatures

    def getWeight(self, key):
        return self.weights.get(key, 0.0)    

    def update(self, state, action, nextState, reward):
        # print("REWARD", reward)
        correction = reward + (self.getDiscountRate() * self.getValue(nextState))
        correction -= self.getQValue(state, action)
        features = self.featExtractor().getFeatures(self, state, action)
        for key in features:
            # self.weights[key] = self.getWeight(key) + self.getAlpha()* correction * features[key]
            self.weights[key] += self.getAlpha() * correction * features[key]

    def getQValue(self, state, action):
        features = self.featExtractor().getFeatures(self, state, action)
        
        dot = [self.getWeight(key) * features[key] for key in features]
        value = sum(dot)
        # self.qValues[(state, action)] = value
        return value

    def getFeatures(self, gameState, action):
        return self.featExtractor().getFeatures(self, gameState, action)

    def final(self, gameState):
        # print('alpha, weights', self.alpha, self.weights)
        print(self.weights)
        return super().final(gameState)
    
    def observationFunction(self, gameState):
        """
        This is where we ended up after our last action.
        """
        if self.lastState is not None:
            reward = self.featExtractor().getReward(self, gameState, self.lastState)
            # Calculate a better reward than difference between state scores self.getScore(state) - self.getScore(lastState)
            self.observeTransition(self.lastState, self.lastAction, gameState, reward) 

class DefensiveFeatures(FeatureExtractor):

    def getReward(self, agent, state, lastState):
        INVADER_REMOVAL_REWARD = 10
        FOOD_LOST_REWARD = -10
        DEATH_REWARD = -100

        reward = 0 
        # the score is changed by 1, based on if food is eaten.
        # i don't think it should earn based off score, since it will give bad data
        reward += agent.getScore(state) - agent.getScore(lastState)

        # check if invader is eaten:

        agentState = state.getAgentState(agent.index)

        currFoodCount= agent.getFoodYouAreDefending(state).count()
        lastFoodCount = agent.getFoodYouAreDefending(lastState).count()
        if currFoodCount < lastFoodCount:
            reward -= FOOD_LOST_REWARD

        enemies = [state.getAgentState(i) for i in agent.getOpponents(state)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]

        lastEnemies = [lastState.getAgentState(i) for i in agent.getOpponents(lastState)]
        lastInvaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]

        if len(invaders) < len(lastInvaders):
            reward += INVADER_REMOVAL_REWARD

        for enemy in enemies:
            agentPos = agentState.getPosition()
            enemyPos = enemy.getPosition()

            if manhattan(agentPos, enemyPos) < 1:
                reward += DEATH_REWARD 
 
            # reward += INVADER_REMOVAL_REWARD

        return reward

    def getFeatures(self, agent, gameState, action):
        features = {}

        walls = gameState.getWalls()
        successor = agent.getSuccessor(gameState, action)
        myState = successor.getAgentState(agent.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0

        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in agent.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        if (len(invaders) > 0):
            #  SCALED BETWEEN 1-0 to avoid exploding weights 
            dists = [agent.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = float(min(dists)) / (walls.getWidth() * walls.getHeight())

        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(agent.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1 

        # scale all features by 1/10
        for feature in features:
            features[feature] /= 10.0
        return features