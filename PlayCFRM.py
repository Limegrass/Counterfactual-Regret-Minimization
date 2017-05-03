KUHN_DECK = [1,2,3]
PLAYER = 0
CPU = 1
PASS = 0
BET = 1
import sys
import random

def main():
	#Dictionary of pass percentage
	cfrmStrategy = {}
	cfrmStrategy['1'] = .765
	cfrmStrategy['1b'] =  1.0
	cfrmStrategy['1p'] =  0.668
	cfrmStrategy['1pb'] =  1.0
	
	cfrmStrategy['2'] =  1.0
	cfrmStrategy['2b'] =  0.666
	cfrmStrategy['2p'] =  1.0
	cfrmStrategy['2pb'] =  0.431
	
	cfrmStrategy['3'] =  0.289
	cfrmStrategy['3b'] =  0.0
	cfrmStrategy['3p'] =  0.0
	cfrmStrategy['3pb'] =  0.0
	
	playerStrategy = {}
	
	while True:
		totalGain = 0.0
		handsPlayed = 0.0
		while True:
			print "Total Earnings: ", totalGain
			if (handsPlayed == 0.0):
				pass
			else:
				print "Hands played: ", int(handsPlayed)
				print "Average Earnings: ", totalGain/handsPlayed
			
			plays = raw_input(
			"Type: 0 to start over, 1 to play a single hands,\n"
			"or type the number of hands to play a mixed strategy\n"
			"To self-play, type \"Nash\"\n"
			"\tInput: "
			)
			if plays == "0":
				break
			while plays == "1":
				print "Total Earnings: ", totalGain
				if (handsPlayed == 0.0):
					pass
				else:
					print "Average Earnings: ", totalGain/handsPlayed
				random.shuffle(KUHN_DECK)
				yourInfo = str(KUHN_DECK[PLAYER])
				print "\tYou have a", yourInfo
				cpuInfo = str(KUHN_DECK[CPU])
				roundCounter = 0
				while kuhnEval(cpuInfo) is None and kuhnEval(yourInfo) is None:
					if roundCounter%2 == 0:
						if roundCounter == 0:
							pass
						else:
							if yourInfo[-1] == "b":
								print "\tYour opponent has bet! \n\tWhat will you do?"
							else: 
								print "\tYour opponent has check/called! \nWhat will you do?"
						#Easier to input with 1 and 2 rather than pb
						decision = raw_input(
						"\tType 1 to check/fold or 2 to bet/call,\n\tq to quit single play\n"#, or s to switch sides\n"
						"\t\tInput: "
						)
						if decision == "q":
							break
							
						
						if decision == "1":	
							cpuInfo += "p"
							yourInfo += "p"
						else: 
							cpuInfo += "b"
							yourInfo += "b"
					else:
						cpuChoice = random.random()
						#print cpuChoice, " ", cfrmStrategy[cpuInfo]
						
						if cpuChoice > cfrmStrategy[cpuInfo]:
							cpuInfo += "b"
							yourInfo += "b"
						else:
							cpuInfo += "p"
							yourInfo += "p"
					roundCounter += 1
				if decision == "q":
					break
				print "\tYou saw", yourInfo
				print "\tYour opponent had a", KUHN_DECK[CPU]
				earnings = kuhnEval(yourInfo)
				totalGain += earnings
				handsPlayed += 1.0
				
					
				print "\n"
			else:
				if plays == "Nash":
					playerStrategy = cfrmStrategy
					plays = raw_input("Type number of iterations: ")
					
				else:
					playerStrategy['1'] = float(raw_input("Enter the percentage you wish to pass seeing a 1: "))
					playerStrategy['1b'] = float(raw_input("Enter the percentage you wish to pass seeing a 1b: "))
					playerStrategy['1p'] = float(raw_input("Enter the percentage you wish to pass seeing a 1p: "))
					playerStrategy['1pb'] = float(raw_input("Enter the percentage you wish to pass seeing a 1pb: "))
					
					playerStrategy['2'] =  float(raw_input("Enter the percentage you wish to pass seeing a 2: "))
					playerStrategy['2b'] = float(raw_input("Enter the percentage you wish to pass seeing a 2b: "))
					playerStrategy['2p'] = float(raw_input("Enter the percentage you wish to pass seeing a 2p: "))
					playerStrategy['2pb'] = float(raw_input("Enter the percentage you wish to pass seeing a 2pb: "))
					
					playerStrategy['3'] = float(raw_input("Enter the percentage you wish to pass seeing a 3: "))
					playerStrategy['3b'] = float(raw_input("Enter the percentage you wish to pass seeing a 3b: "))
					playerStrategy['3p'] = float(raw_input("Enter the percentage you wish to pass seeing a 3p: "))
					playerStrategy['3pb'] = float(raw_input("Enter the percentage you wish to pass seeing a 3pb: "))
					
				for i in range(int(plays)):
					random.shuffle(KUHN_DECK)
					yourInfo = str(KUHN_DECK[PLAYER])
					cpuInfo = str(KUHN_DECK[CPU])
					roundCounter = 0
					while kuhnEval(cpuInfo) is None and kuhnEval(yourInfo) is None:
						if roundCounter%2 == 0:
							if random.random() > playerStrategy[yourInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
							

						else:
							cpuChoice = random.random()
							if random.random() > cfrmStrategy[cpuInfo]:
								cpuInfo += "b"
								yourInfo += "b"
							else:
								cpuInfo += "p"
								yourInfo += "p"
						roundCounter += 1

					earnings = kuhnEval(yourInfo)
					totalGain += earnings
					handsPlayed += 1.0
				
			
def kuhnEval(history):
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
