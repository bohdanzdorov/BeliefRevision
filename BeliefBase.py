import re

import copy
import cnf_py.run as toCNF
from sympy import symbols
import itertools


class BeliefBase:
    def __init__(self) -> None:
        self.beliefBase = dict()
        self.resolvents = []

    def getBeliefBase(self):
        return self.beliefBase
    
    def clearBeliefBase(self):
        self.beliefBase.clear()
    
    def expansion(self, belief, priority):
        self.beliefBase.update({belief : priority})

    def revision(self, belief, priority):
        a, b, c, d = symbols('a b c d')
        if belief in self.beliefBase:
            print("This belief {", belief, "} is already in beliefBase", self.beliefBase)
        else:
            bufferBeliefBase = self.convertBeliefBaseToCNF(self.beliefBase)
            beliefCNF = self.ClauseToCNF(belief)
            # Get array of arrays from each clause between 'AND'
            arrayBelief = self.StringToArrayCNF(beliefCNF)
            if not self.checkForEntailment(arrayBelief, bufferBeliefBase):
                negativeArrayBelief = self.negateBelief(arrayBelief)
                self.beliefBase = copy.deepcopy(self.contraction(negativeArrayBelief))
            self.expansion(belief, priority)
            print("Belief {" + belief + "} was successfully added to the belief base")

    def revisionWithPostulates(self, belief, priority):
        a, b, c, d = symbols('a b c d')

        negatedBelief = "neg(" + belief + ")"
        isNegatedBeliefInBase = False
        if(negatedBelief in self.beliefBase):
            isNegatedBeliefInBase = True

        beliefBaseBufferForPostulates = copy.deepcopy(self.beliefBase)
        
        if belief in self.beliefBase:
            print("This belief {", belief, "} is already in beliefBase", self.beliefBase)
        else: 
            bufferBeliefBase = self.convertBeliefBaseToCNF(self.beliefBase)
            beliefCNF = self.ClauseToCNF(belief)
            # Get array of arrays from each clause between 'AND'
            arrayBelief = self.StringToArrayCNF(beliefCNF)
            if not self.checkForEntailment(arrayBelief, bufferBeliefBase):
                negativeArrayBelief = self.negateBelief(arrayBelief)
                self.beliefBase = copy.deepcopy(self.contraction(negativeArrayBelief))
            self.expansion(belief, priority)      
            print("Belief {" + belief + "} was successfully added to the belief base")
            beliefBaseBufferForPostulates.update({belief : priority}) # for vacuity postulate
        
        #Vacuity postulate
        if(not isNegatedBeliefInBase):
            if(self.beliefBase == beliefBaseBufferForPostulates):
                print("Vacuity postulate passed")
            else:
                print("Vacuity postulate failed")
        #Inclusion postulate
        isInclusionFailed = False
        for key, value in self.beliefBase.items():
            if key not in beliefBaseBufferForPostulates:
                print(key)
                isInclusionFailed = True
                print("Inclusion postulate failed")
                break
        if(not isInclusionFailed):
            print("Inclusion postulate passed")
        #Success postulate
        if(belief in self.beliefBase):
            print("Success postulate passed")
        else:
            print("Success postulate failed")

    def removeBelief(self, belief):
        if belief in self.beliefBase:
            self.beliefBase.pop(belief)

    def contraction(self, newBelief):
        listOfWorlds = self.sum_combinations(self.beliefBase)
        correctWorld = dict()
        maxPriority = 0
        for world in listOfWorlds:
            convertedWorldToCNF = self.convertBeliefBaseToCNF(world)
            if not self.checkForEntailment(newBelief, convertedWorldToCNF):
                totalPriority = 0
                for priority in list(world.values()):
                    totalPriority += priority
                if totalPriority > maxPriority:
                    maxPriority = totalPriority
                    correctWorld = world
        return correctWorld
    
    def sum_combinations(self, d):
        results = []
        keys = list(d.keys())
        for r in range(1, len(keys) + 1):
            for combo in itertools.combinations(keys, r):
                sum_value = sum(d[k] for k in combo)
                results.append({k: d[k] for k in combo})
                results[-1]['sum'] = sum_value
        results.sort(key=lambda x: x['sum'], reverse=True)

        for result in results:
            del result['sum']

        return results
    
    def getBeliefSet(self):
        return self.beliefBase

    # Convert beliefBase into cnf format without repetitions
    def convertBeliefBaseToCNF(self, bufferBeliefBase):
        cnfBeliefBase = []
        for belief in bufferBeliefBase:
            belief = self.ClauseToCNF(belief)
            cnfBelief = self.StringToArrayCNF(belief)
            for partBelief in cnfBelief:
                if cnfBelief not in cnfBeliefBase:
                    cnfBeliefBase.append(partBelief)
        return cnfBeliefBase

    # returns True - inputted belief follows from Belief Base
    # returns False - inputted belief doesn't follow from Belief B
    def checkForEntailment(self, arrayBelief, bufferBeliefBase):
        # negate belief
        negativeBeliefInCNF = self.negateBelief(arrayBelief)
        # Add each clause of belief to buffer belief base
        for eachNegativeSmallPartOfBelief in negativeBeliefInCNF:
            bufferBeliefBase.append(eachNegativeSmallPartOfBelief)
        #print("\n\nNEGATED BELIEF: ", negativeBeliefInCNF, "\n")
        # make resolve each clause with each clause (except when clause1 = clause2)
        while True:
            #print("\nBUFFER BELIEF BASE:", bufferBeliefBase)
            i = 0
            initialJ = 1
            j = initialJ
            new = []
            while i < len(bufferBeliefBase) - 1:
                while j < len(bufferBeliefBase):
                    #print("i=", i, "j=", j)
                    complementaryLiteralFound = self.resolve(bufferBeliefBase[i], bufferBeliefBase[j])
                    #print("COMPLEMENTARY:", complementaryLiteralFound)
                    if complementaryLiteralFound:
                        #print("from", bufferBeliefBase[i], "and", bufferBeliefBase[j], "RESOLVENTS is", self.resolvents)
                        # if buffer Belief Base is unsatisfiable -> belief Base entails belief
                        for resolvent in self.resolvents:
                            #print("RESOLVENT: ", resolvent)
                            if len(resolvent) == 0:
                                return True
                            if resolvent not in new:
                                new.append(resolvent)
                        #print("NEW:", new, "\n")
                    j += 1
                initialJ += 1
                j = initialJ
                i += 1
            # Check for repetition, if found -> the algorithm is infinite loop
            newIsSubsetOfBufferBeliefBase = 0
            for eachSmallPartOfNew in new:
                newIsSubsetOfBufferBeliefBase = 2
                if eachSmallPartOfNew not in bufferBeliefBase:
                    newIsSubsetOfBufferBeliefBase = 1
                    break
            if newIsSubsetOfBufferBeliefBase == 2:
                return False
            # If there is nothing to resolve -> the Belief Base doesn't entail belief
            #print("NEW:", new)
            if len(new) == 0:
                return False
            for eachSmallPartOfNew in new:
                bufferBeliefBase.append(eachSmallPartOfNew)

    # put in 2d array as the parameter
    def negateBelief(self, beliefs):
        negated_beliefs = []
        if (len(beliefs) == 1):
            for i in range(len(beliefs[0])):
                negated_beliefs.append([-beliefs[0][i]])
        else:
            for i in range((len(beliefs))):
                for j in range(len(beliefs[i])):
                    for k in range(i, len(beliefs)):
                        for l in range(len(beliefs[k])):
                            if (k != i):

                                if (beliefs[i][j] == beliefs[k][l]):
                                    if ([-beliefs[i][j]] not in negated_beliefs):
                                        negated_beliefs.append([-beliefs[i][j]])
                                else:
                                    negatedClause = [-beliefs[i][j], -beliefs[k][l]]
                                    negatedClause2 = [-beliefs[k][l], -beliefs[i][j]]
                                    if (negatedClause not in negated_beliefs and negatedClause2 not in negated_beliefs):
                                        negated_beliefs.append(negatedClause)
        return negated_beliefs

    # non-cnf string into cnf string
    def ClauseToCNF(self, clause):
        resultClause = toCNF.run(clause)
        return resultClause[len(resultClause) - 1]

    # cnf string into cnf array
    def StringToArrayCNF(self, cnf_string):
        symbols_list = symbols('a b c d')
        symbol_mapping = {symbol.name: symbol for symbol in symbols_list}
        symbol_mapping_negative = {symbol.name: -symbol for symbol in symbols_list}

        clauses = cnf_string.split(' and ')

        literals = []
        for clause in clauses:
            clause_literals = []
            for match in re.finditer(r'\b(?:neg\s+)?([a-d])\b', clause):
                symbol = match.group(1)
                if match.group(0).startswith('neg'):
                    clause_literals.append(symbol_mapping_negative.get(symbol))
                else:
                    clause_literals.append(symbol_mapping.get(symbol))
            literals.append(clause_literals)

        return literals

    # returns True - if complementary literals were found
    # returns False - if there is anything to resolve
    def resolve(self, clause1, clause2):
        set1 = set(clause1)
        set2 = set(clause2)
        complementaryLiteralFound = False
        self.resolvents.clear()
        for literal in set1:
            if -literal in set2:
                set1Copy = copy.deepcopy(set1) - {literal}
                set2Copy = copy.deepcopy(set2) - {-literal}
                new_clause = (set1Copy | set2Copy)
                self.resolvents.append(list(new_clause))
                complementaryLiteralFound = True
        return complementaryLiteralFound

a, b, c, d = symbols('a b c d')
bb = BeliefBase()

choice = 0
while choice != -1:
    choice = int(input("Please, choose the thing you want to do with the belief base: \n" +
        "1. Print\n" +  
        "2. Expand\n" +
        "3. Check for logical entailment\n"+
        "4. Contraction\n"+
        "5. Revision\n"+
        "6. Revision with postulates\n"
        "7. Clear belief base\n\n"+
        ">> "))
    if(choice == 1):
        print("\nBelief base: ", bb.getBeliefBase(), "\n")
        input("Press any key to continue...\n\n")
    elif(choice == 2):
        newBelief = input("Enter new belief > ")
        newBeliefPriority = int(input("Enter priority > "))
        bb.expansion(newBelief, newBeliefPriority)
        print("\nBelief {", newBelief, "} expanded the belief base!")
        input("Press any key to continue...\n\n")
    elif(choice == 3):
        beliefToCheck = input("Enter belief for checking the logical entailment with current belief base > \n")
        beliefCNF = bb.ClauseToCNF(beliefToCheck)
        arrayBelief = bb.StringToArrayCNF(beliefCNF)
        if(bb.checkForEntailment(arrayBelief, bb.convertBeliefBaseToCNF(bb.getBeliefBase()))):
            print("Belief {"+ beliefToCheck+ "} entails from the current belief base")
        else:
            print("Belief {"+ beliefToCheck+ "} does NOT entails from the current belief base")
        input("Press any key to continue...\n\n")
    elif(choice == 4):
        beliefToContruct = input("Enter belief for contruction of belief base > \n")
        bb.contraction(beliefToContruct)
        print("Contruction with belief {" + beliefToContruct + "} preformed successfully")
        print("Belief base after contruction: ", bb.getBeliefBase())
        input("Press any key to continue...\n\n")
    elif(choice == 5):
        beliefToRevision = input("Enter belief for revision of belief base > \n")
        beliefToRevisionPriority = int(input("Enter the priority of this belief > \n"))
        bb.revision(beliefToRevision, beliefToRevisionPriority)
        print("Belief base after revision: ", bb.getBeliefBase())
        input("Press any key to continue...\n\n")
    elif(choice == 6):
        beliefToRevisionWPostulates = input("Enter belief for revision of belief base > \n")
        beliefToRevisionPriorityWPostulates = int(input("Enter the priority of this belief > \n"))
        bb.revisionWithPostulates(beliefToRevisionWPostulates, beliefToRevisionPriorityWPostulates)
        print("Belief base after revision: ", bb.getBeliefBase())
        input("Press any key to continue...\n\n")
    elif(choice == 7):
        bb.clearBeliefBase()
        print("Belief base was cleared successfully")
