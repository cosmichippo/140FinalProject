import abc

from pacai.agents.learning.reinforcement import ReinforcementAgent
from pacai.core import distanceCalculator
from pacai.util import util
# so far, just copied over CaptureAgent

class ReinforcementCaptureAgent(ReinforcementAgent):

    def __init__(self, index, timeForComputing = 0.1, **kwargs):
        super().__init__(index, **kwargs)

        # Whether or not you're on the red team
        self.red = None

        # Agent objects controlling you and your teammates
        self.agentsOnTeam = None

        # Maze distance calculator
        self.distancer = None

        # A history of observations
        self.observationHistory = []

        # Time to spend each turn on computing maze distances
        self.timeForComputing = timeForComputing


    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.
        """
        super().registerInitialState(gameState) # start recording learning
        self.red = gameState.isOnRedTeam(self.index)
        self.distancer = distanceCalculator.Distancer(gameState.getInitialLayout())

        self.distancer.getMazeDistances()

    def final(self, gameState):
        super().final(gameState)

        self.observationHistory = []

    def registerTeam(self, agentsOnTeam):
        """
        Fills the self.agentsOnTeam field with a list of the
        indices of the agents on your team.
        """

        self.agentsOnTeam = agentsOnTeam
    @abc.abstractmethod
    def getAction(self, gameState):
        """determines what action the game will apply to pacman"""
        pass

    def getFood(self, gameState):
        """
        Returns the food you're meant to eat.
        This is in the form of a `pacai.core.grid.Grid`
        where `m[x][y] = True` if there is food you can eat (based on your team) in that square.
        """

        if (self.red):
            return gameState.getBlueFood()
        else:
            return gameState.getRedFood()

    def getFoodYouAreDefending(self, gameState):
        """
        Returns the food you're meant to protect (i.e., that your opponent is supposed to eat).
        This is in the form of a `pacai.core.grid.Grid`
        where `m[x][y] = True` if there is food at (x, y) that your opponent can eat.
        """

        if (self.red):
            return gameState.getRedFood()
        else:
            return gameState.getBlueFood()

    def getCapsules(self, gameState):
        if (self.red):
            return gameState.getBlueCapsules()
        else:
            return gameState.getRedCapsules()

    def getCapsulesYouAreDefending(self, gameState):
        if (self.red):
            return gameState.getRedCapsules()
        else:
            return gameState.getBlueCapsules()

    def getOpponents(self, gameState):
        """
        Returns agent indices of your opponents. This is the list of the numbers
        of the agents (e.g., red might be 1, 3, 5)
        """

        if self.red:
            return gameState.getBlueTeamIndices()
        else:
            return gameState.getRedTeamIndices()

    def getTeam(self, gameState):
        """
        Returns agent indices of your team. This is the list of the numbers
        of the agents (e.g., red might be the list of 1,3,5)
        """

        if (self.red):
            return gameState.getRedTeamIndices()
        else:
            return gameState.getBlueTeamIndices()

    def getScore(self, gameState):
        """
        Returns how much you are beating the other team by in the form of a number
        that is the difference between your score and the opponents score.
        This number is negative if you're losing.
        """

        if (self.red):
            return gameState.getScore()
        else:
            return gameState.getScore() * -1
    
    def observationFunction(self, state):
        """
        This is where we ended up after our last action.
        """
        
        if self.lastState is not None:
            reward = self.getScore(state) - self.getScore(self.lastState)
            self.observeTransition(self.lastState, self.lastAction, state, reward)

    def getMazeDistance(self, pos1, pos2):
        """
        Returns the distance between two points using the builtin distancer.
        """

        return self.distancer.getDistance(pos1, pos2)

    def getPreviousObservation(self):
        """
        Returns the `pacai.core.gamestate.AbstractGameState` object corresponding to
        the last state this agent saw.
        That is the observed state of the game last time this agent moved,
        this may not include all of your opponent's agent locations exactly.
        """

        if (len(self.observationHistory) <= 1):
            return None

        return self.observationHistory[-2]

    def getCurrentObservation(self):
        """
        Returns the GameState object corresponding this agent's current observation
        (the observed state of the game - this may not include
        all of your opponent's agent locations exactly).

        Returns the `pacai.core.gamestate.AbstractGameState` object corresponding to
        this agent's current observation.
        That is the observed state of the game last time this agent moved,
        this may not include all of your opponent's agent locations exactly.
        """

        if (len(self.observationHistory) == 0):
            return None

        return self.observationHistory[-1]


    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """

        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()

        if (pos != util.nearestPoint(pos)):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor