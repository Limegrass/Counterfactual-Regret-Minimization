import random
PASS = 0
BET = 1
NUM_ACTIONS = 2
KUHN_DECK = [1,2,3]
LEDUC_DECK = [1,1,2,2,3,3]

#Tracks the regret per game stage
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
		elif self.game == "leduc":
			self.cards = LEDUC_DECK
		self.gameTree = {}

	#Trains the AI to decide on an optimal, Nash EQ strategy
	def train(self, iterations):
	#Called from main function, uses saved game type
		#Set initial utility to float zero
		utility = 0.0
		for _ in range(iterations):
			#Randomizes array
			random.shuffle(self.cards)
			#Adds utiity gained after evaluation?
			#The 1.0 are probability to play by the CFR Measurement?
			utility += self.cfr("", 1.0, 1.0, 0)
		#Print Outcome/winnings and each individual percentage to performt hat action
		print("Average utility: ", utility / iterations)
		for gameState in sorted(self.gameTree.keys()):
			print(gameState, self.gameTree[gameState].getAverageStrategy())

	#Calculates one step of Counterfactual regret
	def cfr(self, history, p0, p1, roundCounter):
		#Finds number result of utility gained for play
		result = self.evaluateGame(history)
		plays = len(history)
		currentPlayer = roundCounter%2
		
		#If it was a terminal state, return the result
		if not result is None:
			return result
		
		#Define current player and append to history
		#Why not just track player as a parameter to pass through the recursive call
		if self.game == "kuhn":
			#player = plays % 2
			
			gameState = str(self.cards[currentPlayer]) + history
		elif self.game == "leduc":
			player = plays % 2 if plays <= 2 or history[:2] == "pp" or history[:2] == "bb" else 1 - plays % 2
			if (plays > 2 and (history[:2] == "pp" or history[:2] == "bb")) or (plays > 3 and history[:3] == "pbb"):
				gameState = str(self.cards[currentPlayer]) + str(self.cards[2]) + history
			else:
				gameState = str(self.cards[currentPlayer]) + history


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
		strategy = node.getStrategy(p0 if currentPlayer== 0 else p1)
		utilities = [0.0] * NUM_ACTIONS
		totalUtility = 0.0
		for i in range(NUM_ACTIONS):
			#Update history and recursive call to function to decide next step
			nextHistory = history + ("p" if i == 0 else "b")
			nextRoundCounter = roundCounter
			#Use updated probability to reach the next game state
			if currentPlayer == 0:
				nextP0 = p0 * strategy[i]
				nextP1 = p1
			else:
				nextP0 = p0 
				nextP1 = p1 * strategy[i]

			if roundCounter == 0:
				nextRoundCounter += 1
			elif roundCounter == 1 and nextHistory == "pb":
				nextRoundCounter += 1
			else:
				nextRoundCounter = 0
				
			
			utilities[i] = -self.cfr(nextHistory, nextP0, nextP1, nextRoundCounter)
			
			#Sum resulting utility for each strategy
			totalUtility += utilities[i] * strategy[i]
		for i in range(NUM_ACTIONS):
			#Diff between gain for an action vs total possible gain?
			regret = utilities[i] - totalUtility
			#Regret for choosing that decision
			node.regretSum[i] += regret * (p1 if currentPlayer == 0 else p0)
		return totalUtility

	def getNextPlayer(self, history, roundCounter):
		#Changes players to 0 if new round bb or pbb or pp
		#Changes to player 2 if currentplayer is 0 and the 
		#Bet passes are terminal so it won't matter
		if roundCounter == 0:
			return 1
		else:
			#pp or bb and any pass will make next player 0/terminal state
			if history[-1] == "b":
				if roundCounter == 1:
					return 0
				return 0
			#only pass bet remains
			else:
				return 1
			
		
	
		
	#returns the value of the game if it is terminal
	#else returns None
	def evaluateGame(self, history):
		#Returns earnings if it is a terminal state and using Kuhn Poker
		#Returns None if not terminal
		if self.game == "kuhn":
			return self.kuhnEval(history)
		
		elif self.game == "leduc":
			return self.leducEval(history)
			
		#Returns none if not a game (never a case)
		#Or when not a terminal state (no conditions met to end game)
	
	#Returns the value of the play in Kuhn Poker if it is a terminal state
	def kuhnEval(self, history):
		#Defines the player and opponent for current turn
		plays = len(history)
		if plays < 2:
			return None
		player = plays % 2
		opponent = 1 - player
		
		#If not terminal
		#Same action leads to a showdown
		#Checks the last two moves
		showdown = (history[-1] == history[-2])
		leadingBet = (history[-2]=="b")
		if showdown:
			winner = self.cards[player] > self.cards[opponent]
			if leadingBet:
				return 2 if winner else -2
			return 1 if winner else -1
		#If not leadingBet and showdown, it's a bet pass
		#if not leading bet, it was a pass bet and we should return None
		return 1 if leadingBet else None
	
	#Returns the value of the play in Leduc Poker if it is a terminal state
	def leducEval(self, history):
		plays = len(history)
		if plays <= 2 or history[:2] == "pp" or history[:2] == "bb":
			player = plays % 2
			opponent = 1 - player
		else:
			opponent = plays % 2
			player = 1 - opponent

		passAfterBetRound1 = (history == "bp" or history == "pbp")
		passAfterBetRound2Min = (history == "ppbp" or history == "pppbp")
		passAfterPassRound2Min = history == "pppp"
		#lastActs = history[-2:]
		#showdown = lastAct[0]==lastAct[1]
		
		passAfterBetRound2Max = (history == "pbbbp" or history == "bbbp" or history == "pbbpbp" or history == "bbpbp")
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





def main():
	#Takes input of game type
	trainer = PokerTrainer("kuhn") 
	#Number of trials
	trainer.train(100000)

if __name__ == "__main__":
	main()















