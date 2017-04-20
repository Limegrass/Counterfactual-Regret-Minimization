import random
PASS = 0
BET = 1
NUM_ACTIONS = 2
KUHN_DECK = [1,2,3]
LEDUC_DECK = [1,1,2,2,3,3]

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

class PokerTrainer(object):
	def __init__(self, game):
		self.game = game
		self.gameTree = {}

	def train(self, iterations):
		if self.game == "kuhn":
			cards = KUHN_DECK
		if self.game == "leduc":
			cards = LEDUC_DECK
		utility = 0.0
		for _ in range(iterations):
			random.shuffle(cards)
			utility += self.cfr(cards, "", 1.0, 1.0)
		print("Average utility: ", utility / iterations)
		for gameState in sorted(self.gameTree.keys()):
			print(gameState, self.gameTree[gameState].getAverageStrategy())

	def cfr(self, cards, history, p0, p1):
		result = self.evaluateGame(cards, history, self.game)
		plays = len(history)
		if not result is None:
			return result

		if self.game == "kuhn":
			player = plays % 2
			gameState = str(cards[player]) + history

		if self.game == "leduc":
			player = plays % 2 if plays <= 2 or history[:2] == "pp" or history[:2] == "bb" else 1 - plays % 2
			if (plays > 2 and (history[:2] == "pp" or history[:2] == "bb")) or (plays > 3 and history[:3] == "pbb"):
				gameState = str(cards[player]) + str(cards[2]) + history
			else:
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

	def evaluateGame(self, cards, history, game):
		plays = len(history)
		if game == "kuhn":
			player = plays % 2
			opponent = 1 - player

			passAfterPass = history == "pp"
			passAfterBet = (history == "bp" or history == "pbp")
			doubleBet = (history == "bb" or history == "pbb")
			winner = cards[player] > cards[opponent]

			if passAfterPass:
				return 1 if winner else -1
			if passAfterBet:
				return 1
			if doubleBet:
				return 2 if winner else -2

		if game == "leduc":
			if plays <= 2 or history[:2] == "pp" or history[:2] == "bb":
				player = plays % 2
				opponent = 1 - player
			else:
				opponent = plays % 2
				player = 1 - opponent

			passAfterBetRound1 = (history == "bp" or history == "pbp")
			passAfterBetRound2Min = (history == "ppbp" or history == "pppbp")
			passAfterBetRound2Max = (history == "pbbbp" or history == "bbbp" or history == "pbbpbp" or history == "bbpbp")
			passAfterPassRound2Min = history == "pppp"
			passAfterPassRound2Max = (history == "pbbpp" or history == "bbpp")
			doubleBetRound2Min = (history == "pppbb" or history == "ppbb")
			doubleBetRound2Max = (history == "pbbpbb" or history == "bbpbb" or history == "pbbbb" or history == "bbbb")
			winner = (cards[player] == cards[2] or (cards[opponent] != cards[2] and cards[player] > cards[opponent]))
			tie = cards[player] == cards[opponent]

			if passAfterBetRound1:
				return 1
			if passAfterBetRound2Min:
				return 1
			if passAfterBetRound2Max:
				return 2
			if passAfterPassRound2Min:
				if tie:
					return 0
				return 1 if winner else -1
			if passAfterPassRound2Max:
				if tie:
					return 0
				return 2 if winner else -2
			if doubleBetRound2Min:
				if tie:
					return 0
				return 2 if winner else -2
			if doubleBetRound2Max:
				if tie:
					return 0
				return 4 if winner else -4

		return None



def main():
	trainer = PokerTrainer("kuhn")
	trainer.train(100000)

if __name__ == "__main__":
	main()















