KUHN_DECK = [1,2,3]
PASS = "1"
BET = "2"
import sys
import random
import os

def main():
	#Dictionary of pass percentage
	cfrmKuhnStrategy = {}
	cfrmKuhnStrategy['1'] = .765
	cfrmKuhnStrategy['1b'] =  1.0
	cfrmKuhnStrategy['1p'] =  0.666
	cfrmKuhnStrategy['1pb'] =  1.0
	
	cfrmKuhnStrategy['2'] =  1.0
	cfrmKuhnStrategy['2b'] =  0.666
	cfrmKuhnStrategy['2p'] =  1.0
	cfrmKuhnStrategy['2pb'] =  0.431
	
	cfrmKuhnStrategy['3'] =  0.289
	cfrmKuhnStrategy['3b'] =  0.0
	cfrmKuhnStrategy['3p'] =  0.0
	cfrmKuhnStrategy['3pb'] =  0.0
	
	
	while True:
		totalGain = 0.0
		handsPlayed = 0.0
		PLAYER = 0
		CPU = 1-PLAYER
		while True:
			if PLAYER == 0:
				print "You play first every round!"
			else:
				print "You play second every round!"
			print "Total Earnings: ", totalGain
			if (handsPlayed == 0.0):
				pass
			else:
				print "Hands played: ", int(handsPlayed)
				print "Average Earnings: ", totalGain/handsPlayed
			
			plays = raw_input(
			"Menu:\n\t0: Reset stats\n\t1: Play a single hand"
			"\n\t2: Simulate mixed strategy"
			"\n\t3: Simulate Nash equilibrium strategy"
			"\n\t4: Switch playing order\n"
			"\nInput: "
			)			
			os.system('cls' if os.name == 'nt' else 'clear')

			if plays == "0":
				print "==========================================================="
				print "\tYou played", int(handsPlayed), "hand(s)."
				print "\tYour lifetime total earnings was: ", totalGain
				if(handsPlayed > 0.0):
					print "\tYour lifetime average earnings was: ", totalGain/handsPlayed
				print "==========================================================="
				break

			elif plays == "1":
				while True:
					print "Total Earnings: ", totalGain
					if (handsPlayed == 0.0):
						pass
					else:
						print "Average Earnings: ", totalGain/handsPlayed
					random.shuffle(KUHN_DECK)
					yourInfo = str(KUHN_DECK[PLAYER])
					print "You have a", yourInfo
					cpuInfo = str(KUHN_DECK[CPU])
					roundCounter = 0
					while kuhnEval(cpuInfo, PLAYER, CPU) is None and kuhnEval(yourInfo, PLAYER, CPU) is None:
						if roundCounter%2 == PLAYER:
							if roundCounter == 0:
								pass
							else:
								if yourInfo[-1] == "b":
									print "our opponent has bet! \nWhat will you do?"
								else: 
									print "Your opponent has check/called! \nWhat will you do?"
							#Easier to input with 1 and 2 rather than pb
							decision = raw_input(
							"\tType 1 to check/fold or 2 to bet/call,\n\tq to quit single play\n"#, or s to switch sides\n"
							"Input: "
							)
							if decision == "q":
								break
								
							if decision == PASS:	
								cpuInfo += "p"
								yourInfo += "p"
							else: 
								cpuInfo += "b"
								yourInfo += "b"
						else:
							cpuChoice = random.random()
							#print cpuChoice, " ", cfrmKuhnStrategy[cpuInfo]
							
							if cpuChoice > cfrmKuhnStrategy[cpuInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
						roundCounter += 1
					if decision == "q":
						break
					print
					print "You saw", yourInfo
					print "Your opponent had a", KUHN_DECK[CPU]
					earnings = kuhnEval(yourInfo, PLAYER, CPU) 
					print "Change in your earnings:", earnings
					totalGain += earnings
					handsPlayed += 1.0
					temp = raw_input("Press enter for the next hand")
					#Comment the next time to see full history
					os.system('cls' if os.name == 'nt' else 'clear')
				os.system('cls' if os.name == 'nt' else 'clear')
			elif plays == "2":
				localGain = 0.0
				localHands = 0.0
				playerStrategy = {}
				try:
					plays = int(raw_input("Enter number of interations: "))
				except:
					print "Please enter an positive integer"
					continue
				
				for state in sorted(list(cfrmKuhnStrategy.keys())):
					print "Enter the percentage [0.0, 1.0] you wish to bet seeing a", state,": ",
					while state not in playerStrategy:
						try:
							playerStrategy[state] = float(raw_input())
						except:
							print "Please enter a positive deicmal number: ",
							
				print "Running simulation..."
				for i in range(int(plays)):
					random.shuffle(KUHN_DECK)
					yourInfo = str(KUHN_DECK[PLAYER])
					cpuInfo = str(KUHN_DECK[CPU])
					roundCounter = 0
					while kuhnEval(cpuInfo, PLAYER, CPU) is None and kuhnEval(yourInfo, PLAYER, CPU) is None:
						if roundCounter%2 == PLAYER:
							if random.random() < playerStrategy[yourInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
							

						else:
							cpuChoice = random.random()
							if random.random() > cfrmKuhnStrategy[cpuInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
						roundCounter += 1
					
					earnings = kuhnEval(yourInfo, PLAYER, CPU)
					totalGain += earnings
					localGain += earnings
					localHands += 1.0
					handsPlayed += 1.0
				os.system('cls' if os.name == 'nt' else 'clear')
				print "That strategy netted: ", localGain, "over", localHands, "hands"
				print "With an average earning of", localGain/localHands, "per hand"
				print
				
			elif plays == "3":
				playerStrategy = cfrmKuhnStrategy
				try:
					plays = int(raw_input("Enter number of interations: "))
				except:
					print "Please enter an positive integer"
					continue
				localGain = 0.0
				localHands = 0.0
				print "Running simulation..."
				for i in range(int(plays)):
					random.shuffle(KUHN_DECK)
					yourInfo = str(KUHN_DECK[PLAYER])
					cpuInfo = str(KUHN_DECK[CPU])
					roundCounter = 0
					while kuhnEval(cpuInfo, PLAYER, CPU) is None and kuhnEval(yourInfo, PLAYER, CPU) is None:
						if roundCounter%2 == PLAYER:
							if random.random() > playerStrategy[yourInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
							

						else:
							cpuChoice = random.random()
							if random.random() > cfrmKuhnStrategy[cpuInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
						roundCounter += 1

					earnings = kuhnEval(yourInfo, PLAYER, CPU)
					totalGain += earnings
					localGain += earnings
					localHands += 1.0
					handsPlayed += 1.0
				os.system('cls' if os.name == 'nt' else 'clear')
				print "That strategy netted: ", localGain, "over", localHands, "hands"
				print "With an average earning of", localGain/localHands, "per hand"
				print
			elif plays == "4":
				PLAYER = CPU
				CPU = 1-PLAYER
			else: 
				print "Please enter a valid input."
def kuhnEval(history, PLAYER, CPU):
	#Defines the player and opponent for current turn
	plays = len(history)
	if plays < 2:
		return None
	
	#If not terminal
	#Same action leads to a showdown
	#Checks the last two moves
	showdown = (history[-1] == history[-2])
	leadingBet = (history[-2]=="b")
	if showdown:
		winner = KUHN_DECK[PLAYER] > KUHN_DECK[CPU]
		if leadingBet:
			return 2 if winner else -2
		return 1 if winner else -1
	
	if history[-2:] == "bp":
		return 1 if (plays-1)%2 == PLAYER else -1
	#If not leadingBet and showdown, it's a bet pass
	#if not leading bet, it was a pass bet and we should return None
	return 1 if leadingBet else None

	
	

if __name__ == "__main__":
	main()
