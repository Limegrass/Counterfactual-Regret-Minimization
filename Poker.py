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

	#Returns the least regretful strategy as defined by cfr
	def getStrategy(self, probability):
		sum = 0
		#Sum all positive strategies
		for i in range(NUM_ACTIONS):
			self.strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
			sum += self.strategy[i]
		#Gives percentage to do one strategy over the other
		for i in range(NUM_ACTIONS):
			if sum > 0:
				self.strategy[i] /= sum
			else:
				self.strategy[i] = 1.0 / NUM_ACTIONS
			#probability = percentage chance to reach this game state
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
	#Save game type
	#Initialize a game tree history
	def __init__(self, game):
		self.game = game
		if self.game == "kuhn":
			self.cards = KUHN_DECK
		if self.game == "leduc":
			self.cards = LEDUC_DECK
		self.gameTree = {}

	def train(self, iterations):
	#Called from main function, uses saved game type
		
		#Set initial utility to float zero
		utility = 0.0
		for _ in range(iterations):
			#Randomizes array
			random.shuffle(self.cards)
			#Adds utiity gained after evaluation?
			#The 1.0 are probability to play by the CFR Measurement?
			utility += self.cfr("", 1.0, 1.0)
		#Print Outcome/winnings and each individual percentage to performt hat action
		print("Average utility: ", utility / iterations)
		for gameState in sorted(self.gameTree.keys()):
			print(gameState, self.gameTree[gameState].getAverageStrategy())

	def cfr(self, history, p0, p1):
		#Finds number result of utility gained for play
		result = self.evaluateGame(history)
		plays = len(history)
		
		#If it was a terminal state, return the result
		if not result is None:
			return result
		
		#Define current player and append to history
		if self.game == "kuhn":
			player = plays % 2
			gameState = str(self.cards[player]) + history

		if self.game == "leduc":
			player = plays % 2 if plays <= 2 or history[:2] == "pp" or history[:2] == "bb" else 1 - plays % 2
			if (plays > 2 and (history[:2] == "pp" or history[:2] == "bb")) or (plays > 3 and history[:3] == "pbb"):
				gameState = str(self.cards[player]) + str(self.cards[2]) + history
			else:
				gameState = str(self.cards[player]) + history


		#If the current game state has already existed
		#Then create a pointer to the node for the same state
		if gameState in self.gameTree:
			node = self.gameTree[gameState]
		#Else create the state for the current game state
		else:
			node = gameTreeNode(gameState)
			self.gameTree[gameState] = node
		#Tells what strategy to play
		#0 if pass, else bet
		strategy = node.getStrategy(p0 if player == 0 else p1)
		utilities = [0.0] * NUM_ACTIONS
		totalUtility = 0.0
		for i in range(NUM_ACTIONS):
			#Update history and recursive call to function to decide next step
			nextHistory = history + ("p" if i == 0 else "b")
			#Use updated probability to reach the next game state
			if player == 0:
				utilities[i] = - self.cfr(nextHistory, p0 * strategy[i], p1)
			else:
				utilities[i] = - self.cfr(nextHistory, p0, p1 * strategy[i])
			#Sum resulting utility for each strategy
			totalUtility += utilities[i] * strategy[i]
		for i in range(NUM_ACTIONS):
			#Diff between gain for an action vs total possible gain?
			regret = utilities[i] - totalUtility
			#Regret for choosing that decision
			node.regretSum[i] += regret * (p1 if player == 0 else p0)
		return totalUtility

	def evaluateGame(self, history):
		#Number of moves made
		plays = len(history)
		
		#Returns earnings if it is a terminal state and using Kuhn Poker
		if self.game == "kuhn":
			#Defines the player and opponent for current turn
			player = plays % 2
			opponent = 1 - player

			#Finds which sequence of moves was conducted
			passAfterPass = history == "pp"
			passAfterBet = (history == "bp" or history == "pbp")
			doubleBet = (history == "bb" or history == "pbb")
			#winner is true if player wins
			winner = self.cards[player] > self.cards[opponent]

			if passAfterPass:
				return 1 if winner else -1
			if passAfterBet:
				return 1
			if doubleBet:
				return 2 if winner else -2

		if self.game == "leduc":
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
			winner = (self.cards[player] == self.cards[2] or (self.cards[opponent] != self.cards[2] and self.cards[player] > self.cards[opponent]))
			tie = self.cards[player] == self.cards[opponent]

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
			
			
		#Returns none if not a game (never a case)
		#Or when not a terminal state (no conditions met to end game)
		return None



def main():
	#Takes input of game type
	trainer = PokerTrainer("kuhn") 
	#Number of trials
	trainer.train(100000)

if __name__ == "__main__":
	main()















