import random
PASS = 0
BET = 1
NUM_ACTIONS = 2

class gameTreeNode(object):
	"""
	gameState - Players card and history of actions taken
	regretSum - Total regret for opponent for moves not selected to reach gameState
	strategy - Actions weighted to make opponent regret equal for all actions
	strategySum - Total strategy for each action accumulated over iterations

	"""
	def __init__(self, gameState = ""):
		self.gameState = gameState
		self.regretSum = [0.0] * NUM_ACTIONS
		self.strategy = [0.0] * NUM_ACTIONS
		self.strategySum = [0.0] * NUM_ACTIONS

	def getStrategy(self, probability):
		sum = 0
		for i in range(NUM_ACTIONS):
			self.strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
			sum += self.strategy[i]
		for i in range(NUM_ACTIONS):
			if sum > 0:
				self.strategy[i] /= sum
			else:
				self.strategy[i] = 1.0 / NUM_ACTIONS
			self.strategySum[i] += self.strategy[i] * probability
		return self.strategy

	def getAverageStrategy(self):
		averageStrategy = [0.0] * NUM_ACTIONS
		sum = 0
		for i in range(NUM_ACTIONS):
			sum += self.strategySum[i]
		for i in range(NUM_ACTIONS):
			if sum > 0:
				averageStrategy[i] = self.strategySum[i] / sum
			else:
				averageStrategy[i] = 1.0 / NUM_ACTIONS
		return averageStrategy

class kuhnPokerTrainer(object):
	def __init__(self):
		self.gameTree = {}

	def train(self, iterations):
		cards = [1,2,3]
		utility = 0.0
		for _ in range(iterations):
			random.shuffle(cards)
			utility += self.cfr(cards, "", 1.0, 1.0)
		print("Average utility: ", utility / iterations)
		for gameState in sorted(self.gameTree.keys()):
			print(gameState, self.gameTree[gameState].getAverageStrategy())

	def cfr(self, cards, history, p0, p1):
		plays = len(history)
		player = plays % 2
		opponent = 1 - player
		#Check for terminal game states
		if plays > 1:
			passAfterPass = history[-2:] == "pp"
			passAfterBet = history[-2:] == "bp"
			doubleBet = history[-2:] == "bb"
			winner = cards[player] > cards[opponent]
			if passAfterPass:
				return 1 if winner else -1
			elif passAfterBet:
				return 1
			elif doubleBet:
				return 2 if winner else -2
		#Update game tree
		gameState = str(cards[player]) + history
		if gameState in self.gameTree:
			node = self.gameTree[gameState]
		else:
			node = gameTreeNode(gameState)
			self.gameTree[gameState] = node
		strategy = node.getStrategy(p0 if player == 0 else p1)
		utilities = [0.0] * NUM_ACTIONS
		totalUtility = 0.0
		for i in range(NUM_ACTIONS):
			nextHistory = history + ("p" if i == 0 else "b")
			if player == 0:
				utilities[i] = - self.cfr(cards, nextHistory, p0 * strategy[i], p1)
			else:
				utilities[i] = - self.cfr(cards, nextHistory, p0, p1 * strategy[i])
			totalUtility += utilities[i] * strategy[i]
		for i in range(NUM_ACTIONS):
			regret = utilities[i] - totalUtility
			node.regretSum[i] += regret * (p1 if player == 0 else p0)
		return totalUtility

def main():
	trainer = kuhnPokerTrainer()
	trainer.train(1000000)

if __name__ == "__main__":
	main()















