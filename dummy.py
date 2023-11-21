import random

from pacai.agents.capture.capture import CaptureAgent
from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.core.distance import manhattan

class DummyAgent(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        newPosition = successor.getAgentPosition(self.index)
        curFood = successor.getFood()

        score = 0
        food_distance = list()
        for food_pos in curFood.asList():
            food_distance.append(manhattan(newPosition, food_pos))
        if food_distance:
            min_food_dist = min(food_distance)

        # reciprocal of food and ghost distance
        features['foodDistance'] = 1 / (min_food_dist + 0.1)
        if action == 'Stop':
            score -= 5.0
        features['successorScore'] = successor.getScore()
        return features

    def getWeights(self, gameState, action):
        return {
            'foodDistance' : 10,
            'successorScore': 1
        }
