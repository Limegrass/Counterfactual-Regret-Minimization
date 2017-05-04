import random
import sys
PASS = 0
BET = 1
RERAISE = 2
#Change NUM_ACTIONS to 2 if no reraises allowed
#NUM_ACTIONS = 3
NUM_ACTIONS = 3
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
    def __init__(self, gameState, numChoices):
        self.gameState = gameState
        self.actions = numChoices
        self.regretSum = [0.0] * numChoices
        self.strategy = [0.0] * numChoices
        self.strategySum = [0.0] * numChoices

    #Returns the least regretful strategy as defined by cfr
    def getStrategy(self, probability):
        sum = 0
        #Sum all positive strategies
        for i in range(self.actions):
            self.strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
            sum += self.strategy[i]
        #Gives percentage to do one strategy over the other
        for i in range(self.actions):
            if sum > 0:
                self.strategy[i] /= sum
            else:
                self.strategy[i] = 1.0 / self.actions
            #probability = percentage chance to reach this game state
            self.strategySum[i] += self.strategy[i] * probability
        return self.strategy

    def getAverageStrategy(self):
        averageStrategy = [0.0] * self.actions
        sum = 0
        for i in range(self.actions):
            sum += self.strategySum[i]
        for i in range(self.actions):
            if sum > 0:
                averageStrategy[i] = self.strategySum[i] / sum
            else:
                averageStrategy[i] = 1.0 / self.actions
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
            utility += self.cfr("", 1.0, 1.0, 0, False)
            #print utility
        #Print Outcome/winnings and each individual percentage to performt hat action
        print "Iterations:", iterations
        print("Average utility: ", utility / iterations)
        print("Strategy:")
        for gameState in sorted(self.gameTree.keys()):
            averageStrategy = self.gameTree[gameState].getAverageStrategy()
            sys.stdout.write("State:" + "%10s"%gameState + "\t\t")
            for i in range(len(averageStrategy)):
                if i == PASS:
                    sys.stdout.write("Pass: " + "%6.3f" % (averageStrategy[i]) + "\t\t"),
                if i == BET:
                    sys.stdout.write("Bet: " +  "%6.3f" % (averageStrategy[i]) + " \t\t"),
                if i == RERAISE:
                    sys.stdout.write("Raise: " + "%6.3f" % (averageStrategy[i]) + "\t\t"),
            print


    #Calculates one step of Counterfactual regret
    def cfr(self, history, p0, p1, roundCounter, stage2):
        #Finds number result of utility gained for play
        result = self.evaluateGame(history)
        plays = len(history)
        currentPlayer = roundCounter%2
        #print history, "", currentPlayer

        #If it was a terminal state, return the result

        if not result is None:
            return result

        #Define current player and append to history
        #Why not just track player as a parameter to pass through the recursive call
        if self.game == "kuhn":
            #player = plays % 2

            gameState = str(self.cards[currentPlayer]) + history
        elif self.game == "leduc":
            #player = plays % 2 if plays <= 2 or history[:2] == "pp" or history[:2] == "bb" else 1 - plays % 2
            if not stage2:
                gameState = str(self.cards[currentPlayer]) + history
            else:
            #if plays > 2 and (history[:2] == "pp" or history[:2] == "bb" or plays > 3 and history[:3] == "pbb" or history[:3] == "brb" or history[:4] == "pbrb"):
                gameState = str(self.cards[currentPlayer]) + str(self.cards[2]) + history
            #else:
                #gameState = str(self.cards[currentPlayer]) + history



        #If the current game state has already existed
        #Then create a pointer to the node for the same state
        actions = 2
        if (roundCounter == 1 or roundCounter == 2) and history[-1]== "b":
            actions = NUM_ACTIONS
        if gameState in self.gameTree:
            node = self.gameTree[gameState]
        #Else create the state for the current game state
        else:

            node = gameTreeNode(gameState, actions)
        utilities = [0.0] * actions
        self.gameTree[gameState] = node

        #Returns the percentage to reach the next strategy steps.
        strategy = node.getStrategy(p0 if currentPlayer == 0 else p1)
        totalUtility = 0.0
        for i in range(actions):
            #Update history and recursive call to function to decide next step
            nextHistory = history 
            nextStage = stage2
            if i == PASS:
                nextHistory += "p"
            elif i == BET:
                nextHistory += "b"
            elif i == RERAISE:
                nextHistory += "r"
            else: 
                return None

            #Use updated probability to reach the next game state
            if currentPlayer == 0:
                nextP0 = p0 * strategy[i]
                nextP1 = p1
            else:
                nextP0 = p0 
                nextP1 = p1 * strategy[i]

            #Update the turn counter so we know the player
            nextRoundCounter = roundCounter
            if  (nextHistory[-2:] == "pp" or nextHistory[-2:] == "bb" or nextHistory[-2:] == "rb") and roundCounter != 0:
            #if (history[:3] == "pbb" or history[:3] =="brb"):
                nextRoundCounter = 0
            else:
                nextRoundCounter += 1



            if nextRoundCounter == 0:
                nextStage = True
            utilities[i] = -self.cfr(nextHistory, nextP0, nextP1, nextRoundCounter, nextStage)

            #Sum resulting utility for each strategy
            totalUtility += utilities[i] * strategy[i]
        for i in range(actions):
            #Diff between gain for an action vs total possible gain?
            regret = utilities[i] - totalUtility
            #Regret for choosing that decision
            node.regretSum[i] += regret * (p1 if currentPlayer == 0 else p0)

        return totalUtility



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
        if plays < 2:
            return None

        #Terminal in round 1, so we can shortcircuit 
        #vars for readability
        round1bp = (history[:2] == "bp") or (history[:3] == "pbp")
        if(round1bp):
            return 1

        round1brp = (history[:3] == "brp") or (history[:4] == "pbrp")
        if(round1brp):
            return 3

        #Not terminal in round 1
        #Round 1 is just checks
        round1pp = (history[:2] == "pp")
        #Create var, updated only if not pp. Reduces linear checks
        round1bb = False
        round1br = False
        #Default to pp pot size and index
        round2startIndex = 2
        round1pot = 1
        #Round1 is a bet call
        if not round1pp:
            round1bb = (history[:2] == "bb") or (history[:3] == "pbb")
            leadingPass = history[0] == "p"
            if round1bb:
                if leadingPass:
                    round2startIndex = 3
                round1pot = 3
            else:
                round1br = (history[:3] == "brb") or (history[:4] == "pbrb")
                if round1br:
                    #PBRB
                    if leadingPass:
                        round2startIndex = 4
                    #Only one nonterminal state left, 3
                    else:
                        round2startIndex = 3
                    round1pot = 5

        #Round 1 unfinished (eg only 1 move is done)
        if not (round1pp or round1bb or round1br):
            return None


        round2History = history[round2startIndex:]

        round2Plays = len(round2History)
        if plays - round2Plays < 2:
            return None

        #Bet pass in round 2
        round2bp = (round2History == "bp") or (round2History == "pbp")
        if(round2bp):
            return round1pot

        #Bet raise pass in round 2
        round2brp = (round2History == "brp") or (round2History == "pbrp")
        if(round2brp):
            return 4+round1pot

        player = round2Plays%2
        opponent = 1-player

        winner = (self.cards[player] == self.cards[2] or (self.cards[opponent] != self.cards[2] and self.cards[player] > self.cards[opponent]))
        tie = self.cards[player] == self.cards[opponent]
        #Check to showdown
        round2pp = (round2History == "pp")
        if round2pp: 
            if tie:
                return 0
            return round1pot if winner else -round1pot

        #Bet to showdown
        round2bb = (round2History == "bb") or (round2History == "pbb")
        if round2bb:
            if tie:
                return 0
            return 4+round1pot if winner else -(4+round1pot)

        #Betraise to showdown
        round2br = (round2History == "brb") or (round2History == "pbrb")
        if round2br: 
            if tie:
                return 0
            return 8+round1pot if winner else -(8+round1pot)









def main():
    #Takes input of game type
    trainer = PokerTrainer("leduc") 
    #Number of trials
    trainer.train(100000)

if __name__ == "__main__":
    main()
