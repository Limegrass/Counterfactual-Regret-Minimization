import random
PASS = 0
BET = 1
NUM_ACTIONS = 2
KUHN_DECK = [1,2,3]
LEDUC_DECK = [1,1,2,2,3,3]

class gameTreeNode(object):
  """
  gameState - Players card and history of actions taken
  regretSum - Total regret for not selecting move in prior instances of gameState
  strategy - Actions weighted by normalized positive regretSum
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
    self.cards = KUHN_DECK if game == "kuhn" else LEDUC_DECK

  def train(self, iterations):
    utility = 0.0
    for _ in range(iterations):
      random.shuffle(self.cards)
      utility += self.cfr("", 1.0, 1.0)
    print("Average utility: ", utility / iterations)
    print("Strategy:")
    for gameState in sorted(self.gameTree.keys()):
      print("State: %8s  Pass: %6.3f  Bet: %6.3f" % (gameState,
            self.gameTree[gameState].getAverageStrategy()[0],
            self.gameTree[gameState].getAverageStrategy()[1]))

  def cfr(self, history, p0, p1):
    player = self.getCurrentPlayer(history)
    result = self.evaluateGame(history, player)
    if not result is None:
      return result

    gameState = self.getGameState(history, player)

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
        utilities[i] = - self.cfr(nextHistory, p0 * strategy[i], p1)
      else:
        utilities[i] = - self.cfr(nextHistory, p0, p1 * strategy[i])
      totalUtility += utilities[i] * strategy[i]
    for i in range(NUM_ACTIONS):
      regret = utilities[i] - totalUtility
      node.regretSum[i] += regret * (p1 if player == 0 else p0)
    return totalUtility

  def getCurrentPlayer(self, history):
    if self.game == "kuhn":
      return len(history) % 2
    else:
      plays = len(history)
      return plays % 2 if plays <= 2 or history[:2] == "pp" or history[:2] == "bb" else 1 - (plays % 2)

  def getGameState(self, history, currentPlayer):
    if self.game == "kuhn":
      return str(self.cards[currentPlayer]) + history
    else:
      plays = len(history)
    if (plays > 2 and (history[:2] == "pp" or history[:2] == "bb")) or plays > 3:
      return str(self.cards[currentPlayer]) + str(self.cards[2]) + history
    else:
      return str(self.cards[currentPlayer]) + history

  def evaluateGame(self, history, currentPlayer):
    if self.game == "kuhn":
        return self.evaluateKuhn(history, currentPlayer)
    else:
        return self.evaluateLeduc(history, currentPlayer)

  def evaluateKuhn(self, history, currentPlayer):
    passAfterPass = history == "pp"
    passAfterBet = (history == "bp" or history == "pbp")
    doubleBet = (history == "bb" or history == "pbb")
    winner = self.cards[currentPlayer] > self.cards[1 - currentPlayer]

    if passAfterPass:
      return 1 if winner else -1
    if passAfterBet:
      return 1
    if doubleBet:
      return 2 if winner else -2
    return None

  def evaluateLeduc(self, history, currentPlayer):
    passAfterBetRound1 = (history == "bp" or history == "pbp")
    passAfterBetRound2Min = (history == "ppbp" or history == "pppbp")
    passAfterBetRound2Max = (history == "pbbbp" or history == "bbbp" or history == "pbbpbp" or history == "bbpbp")
    passAfterPassRound2Min = history == "pppp"
    passAfterPassRound2Max = (history == "pbbpp" or history == "bbpp")
    doubleBetRound2Min = (history == "pppbb" or history == "ppbb")
    doubleBetRound2Max = (history == "pbbpbb" or history == "bbpbb" or history == "pbbbb" or history == "bbbb")
    winner = (self.cards[currentPlayer] == self.cards[2] or (self.cards[1 - currentPlayer] != self.cards[2] and self.cards[currentPlayer] > self.cards[1 - currentPlayer]))
    tie = self.cards[currentPlayer] == self.cards[1 - currentPlayer]

    if passAfterBetRound1:
    	return 1
    if passAfterBetRound2Min:
    	return 1
    if passAfterBetRound2Max:
    	return 2
    if passAfterPassRound2Min:
    	return 0 if tie else 1 if winner else -1
    if passAfterPassRound2Max:
    	return 0 if tie else 2 if winner else -2
    if doubleBetRound2Min:
    	return 0 if tie else 2 if winner else -2
    if doubleBetRound2Max:
    	return 0 if tie else 4 if winner else -4

    return None

def main():
  trainer = PokerTrainer("kuhn")
  trainer.train(1000000)

if __name__ == "__main__":
  main()











