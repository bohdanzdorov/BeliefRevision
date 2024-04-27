import copy
import re

from numpy import unique

import cnf_py.run as toCNF
from sympy import symbols

class BeliefBase:
    def __init__(self) -> None:
        self.beliefBase = dict()
        self.resolvents = []
    
    def addBelief(self, belief, priority):
        # a, b, c, d = symbols('a b c d')
        # self.beliefBase.update({"b imp neg c" : 0})
        # self.beliefBase.update({"neg c" : 0})
        # self.beliefBase.update({"neg b" : 0})
        if self.checkForEntailment(belief):
            print("Belief Base ", self.beliefBase, "entails belief", belief)
        else:
            print("Belief Base ", self.beliefBase, "doesn't entail belief", belief)
    def removeBelief(self,belief):
        if belief in self.beliefBase:
            self.beliefBase.remove(belief)

    def getBeliefSet(self):
        return self.beliefBase
    
    #Convert beliefBase into cnf format without repetitions
    def convertBeliefBaseToCNF(self):
        cnfBeliefBase = []
        for belief in self.beliefBase:
            belief = self.ClauseToCNF(belief)
            cnfBelief = self.StringToArrayCNF(belief)
            for partBelief in cnfBelief:
                if(cnfBelief not in cnfBeliefBase):
                    cnfBeliefBase.append(partBelief)
        return cnfBeliefBase

    # returns True - inputted belief follows from Belief Base
    # returns False - inputted belief doesn't follow from Belief Base
    def checkForEntailment(self, belief):
        if belief in self.beliefBase:
            print("This belief {", belief, "} is already in beliefBase", self.beliefBase)
            return False

        bufferBeliefBase = self.convertBeliefBaseToCNF()
        beliefCNF = self.ClauseToCNF(belief)
        # Get array of arrays from each clause between 'AND'
        arrayBelief = self.StringToArrayCNF(beliefCNF)
        #negate belief
        negativeBeliefInCNF = self.negateBelief(arrayBelief)
        #Add each clause of belief to buffer belief base
        for eachNegativeSmallPartOfBelief in negativeBeliefInCNF:
            bufferBeliefBase.append(eachNegativeSmallPartOfBelief)
        print("\n\nNEGATED BELIEF: ", negativeBeliefInCNF, "\n")
        #make resolve each clause with each clause (except when clause1 = clause2)
        while(True):
            print("\nBUFFER BELIEF BASE:", bufferBeliefBase)
            i = 0
            initialJ = 1
            j = initialJ
            new = []
            while i < len(bufferBeliefBase) - 1:
                while j < len(bufferBeliefBase):
                    print("i=", i, "j=", j)
                    complementaryLiteralFound = self.resolve(bufferBeliefBase[i], bufferBeliefBase[j])
                    print("COMPLEMENTARY:", complementaryLiteralFound)
                    if complementaryLiteralFound:
                        print("from", bufferBeliefBase[i], "and", bufferBeliefBase[j], "RESOLVENTS is", self.resolvents)
                        #if buffer Belief Base is unsatisfaible -> belief Base entails belief
                        if len(self.resolvents) == 0:
                            return True
                        new.append(self.resolvents)
                        print("NEW:", new, "\n")
                    j += 1
                initialJ += 1
                j = initialJ
                i += 1
            #Check for repetition, if found -> the algorithm is infinite loop
            for eachSmallPartOfNew in new:
                if eachSmallPartOfNew in bufferBeliefBase:
                    return False
            #If there is nothing to resolve -> the Belief Base doesn't entail belief
            if len(new) == 0:
                return False
            for eachSmallPartOfNew in new:
                bufferBeliefBase.append(eachSmallPartOfNew)

    # put in 2d array as the parameter
    def negateBelief(self, beliefs):
        symbols_list = symbols('a b c d')
        symbol_mapping_negative = {symbol: -symbol for symbol in symbols_list}
        symbol_mapping_negative.update({-symbol: symbol for symbol in symbols_list})
        negated_beliefs = [[symbol_mapping_negative.get(symbol, symbol) for symbol in row] for row in beliefs]
        return negated_beliefs  

    # non-cnf string into cnf string
    def ClauseToCNF(self, clause):
        resultClause = toCNF.run(clause)
        return resultClause[len(resultClause)-1]
    
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

    #returns True - if complementary literals were found
    #returns False - if there is anything to resolve
    def resolve(self, clause1, clause2):
        set1 = set(clause1)
        set2 = set(clause2)
        complementaryLiteralFound = False

        for literal in set1:
            if -literal in set2:
                set1 = set1 - {literal}
                set2 = set2 - {-literal}
                complementaryLiteralFound = True
                break
        if complementaryLiteralFound:
            new_clause = (set1 | set2)
            self.resolvents = copy.deepcopy(list(new_clause))
        return complementaryLiteralFound



a, b, c, d = symbols('a b c d')

bb = BeliefBase()

#print(bb.resolve([b, -a], [-a]))

#print(bb.StringToArrayCNF(bb.ClauseToCNF("a imp b")))
#bb.addBelief("a", 2)
#bb.addBelief("neg b", 1)
bb.addBelief("b", 1000)
#bb.addBelief("c", 1000)
#print(bb.getBeliefSet())