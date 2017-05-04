KUHN_DECK = [1,2,3]
PASS = "1"
BET = "2"
import sys
import random
import os
import time

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
            os.system('clear')
            print "=================================================="
            print " _  __     _             _____      _             "
            print "| |/ /    | |           |  __ \    | |            "
            print "| ' /_   _| |__  _ __   | |__) |__ | | _____ _ __ "
            print "|  <| | | | '_ \| '_ \  |  ___/ _ \| |/ / _ \ '__|"
            print "| . \ |_| | | | | | | | | |  | (_) |   <  __/ |   "
            print "|_|\_\__,_|_| |_|_| |_| |_|   \___/|_|\_\___|_|   "
            print "=================================================="                                                  

            if PLAYER == 0:
                print "You are Player 1!"
            else:
                print "You are Player 2!"
            print "Total Earnings: ", totalGain
            if (handsPlayed == 0.0):
                pass
            else:
                print "Hands played: ", int(handsPlayed)
                print "Average Earnings: ", totalGain/handsPlayed
            
            plays = raw_input(
            "Menu:"
            "\n\t1: Play"
            "\n\t2: Simulate custom mixed strategy"
            "\n\t3: Simulate Nash equilibrium strategy"
            "\n\t4: Change players"
            "\n\t5: Reset stats"
            "\n\t6: Quit\n"
            "\nInput: "
            )            
            os.system('cls' if os.name == 'nt' else 'clear')

            
            if plays == "1":
                while True:
                    print "Total Earnings: ", totalGain
                    if (handsPlayed == 0.0):
                        pass
                    else:
                        print "Average Earnings: ", totalGain/handsPlayed
                    random.shuffle(KUHN_DECK)
                    yourInfo = str(KUHN_DECK[PLAYER])
                    print "You have ", yourInfo
                    cpuInfo = str(KUHN_DECK[CPU])
                    roundCounter = 0
                    while kuhnEval(cpuInfo, PLAYER, CPU) is None and kuhnEval(yourInfo, PLAYER, CPU) is None:
                        if roundCounter%2 == PLAYER:
                            if roundCounter == 0:
                                pass
                            else:
                                if yourInfo[-1] == "b":
                                    print "\nYour opponent has bet! \nWhat will you do?"
                                else: 
                                    print "\nYour opponent has passed! \nWhat will you do?"
                            #Easier to input with 1 and 2 rather than pb
                            decision = raw_input(
                            "Menu:"
                            "\n\t1: Pass"
                            "\n\t2: Bet"
                            "\n\t3: Quit\n"
                            "\nInput: " 
                            )
                            if decision == "3":
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
                    if decision == "3":
                        break
                    print
                    print "The action sequence was ", yourInfo[1:]
                    print "Your opponent had a", KUHN_DECK[CPU]
                    earnings = kuhnEval(yourInfo, PLAYER, CPU) 
                    print "Change in your earnings:", earnings
                    totalGain += earnings
                    handsPlayed += 1.0
                    temp = raw_input("\nPress enter for the next hand.\n")
                    #Comment the next time to see full history
                    os.system('cls' if os.name == 'nt' else 'clear')
                os.system('cls' if os.name == 'nt' else 'clear')
            elif plays == "2":
                localGain = 0.0
                localHands = 0.0
                playerStrategy = {}
                try:
                    plays = int(raw_input("Enter number of interations: "))
                    if plays < 1:
                    	break
                except:
                    print "Please enter an positive integer"
                    continue
                
                for state in sorted(list(cfrmKuhnStrategy.keys())):
                	if len(state) % 2 != PLAYER:
                		print "Enter the percentage of the time (between 0 and 1) to bet when the game state is", state,": ",
                		while state not in playerStrategy:
                			try:
                				playerStrategy[state] = float(raw_input())
                			except:
                				print "Please enter a number between o and 1: ",
                            
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

            elif plays == "5":
                print "==========================================================="
                print "\tYou played", int(handsPlayed), "hand(s)."
                print "\tYour lifetime total earnings was: ", totalGain
                if(handsPlayed > 0.0):
                    print "\tYour lifetime average earnings was: ", totalGain/handsPlayed
                print "==========================================================="
                time.sleep(5)
                break

            elif plays == "6":
                exit()
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