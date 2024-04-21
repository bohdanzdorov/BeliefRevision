import re
import cnf_py.run as toCNF
from sympy import symbols

class BeliefBase:
    def __init__(self) -> None:
        self.beliefBase = []
    
    def addBelief(self,belief):
        #Transform logical cluase into logical clause in cnf format
        beliefCNF = self.ClauseToCNF(belief)
        #Get array of arrays from each clause between 'AND'
        arrayBelief = self.StringToArrayCNF(beliefCNF)
        #To forbidden adding same values 
        if(arrayBelief in self.beliefBase):
            return False
        
        for orSequence in arrayBelief:
            if(self.checkForContradiction(orSequence)):
                print("Contradiction found!!!!")
                return False
        
        print("WHOLE BELIEF WAS ADDED")
        self.beliefBase.append(belief)
            
    def removeBelief(self,belief):
        if belief in self.beliefBase:
            self.beliefBase.remove(belief)

    def getBeliefSet(self):
        return self.beliefBase
    
    #Convert beliefBase into cnf format without repetitions
    def convertBeliefBaseToCNF(self):
        cnfBeliefBase = []
        for belief in self.beliefBase:
            cnfBelief = self.StringToArrayCNF(belief)
            for partBelief in cnfBelief:
                if(cnfBelief not in cnfBeliefBase):
                    cnfBeliefBase.append(partBelief)
        return cnfBelief

    def checkForContradiction(self, newBelief):
        print("NEW BELIEF: ", newBelief)

        if(len(self.beliefBase) == 0):
            print("BELIEF WAS ADDED AS THE FIRST ELEMENT IN THE BELIEF BASE")
            return False
        
        newBelief = self.negateBelief([newBelief])
        bufferBeliefBase = self.convertBeliefBaseToCNF()
        print("NEGATED NEW BELIEF: ", newBelief, " BELIEF BASE: ", bufferBeliefBase, "\n")

        resolvedInLastIteration = True

        while(resolvedInLastIteration == True and len(bufferBeliefBase) > 0):
            for i in range(len(bufferBeliefBase)):
                print("BELIEF BASE AFTER RESOLVING: ", bufferBeliefBase)
                print("TOKEN FROM BELIEF BASE: ", bufferBeliefBase[i])
                print("NEW BELIEF: ", newBelief[0])

                resolveResult = self.resolve(newBelief[0], bufferBeliefBase[i])
                if(resolveResult is not False): 
                    if(len(resolveResult) == 0):
                        print("RESOLVED WITH SUCCESS , EMPTY BRACKET APPEAR\n")
                        return False
                    elif(len(resolveResult) > 0):
                        print("RESOLVED WITH SUCCESS ", resolveResult, "\n")
                        newBelief = [resolveResult]
                        resolvedInLastIteration = True
                        bufferBeliefBase.pop(i)   
                        break
                else:
                    print("PAIR CANNOT BE RESOLVED\n")
                    resolvedInLastIteration = False
        if(bufferBeliefBase == []):
            return False
        return True

    def negateBelief(self, beliefs):
        symbols_list = symbols('a b c d')
        symbol_mapping_negative = {symbol: -symbol for symbol in symbols_list}
        symbol_mapping_negative.update({-symbol: symbol for symbol in symbols_list})
        negated_beliefs = [[symbol_mapping_negative.get(symbol, symbol) for symbol in row] for row in beliefs]
        return negated_beliefs

    def ClauseToCNF(self, clause):
        resultClause = toCNF.run(clause)
        return resultClause[len(resultClause)-1]
    
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

    def resolve(self, clause1, clause2):
        set1 = set(clause1)
        set2 = set(clause2)
        Have_same_item_flag = 0

        for literal in set1:
            print(literal)
            if -literal in set2:

                set1=set1- {literal}
                set2=set2 - {-literal}
            elif literal in set2:
                Have_same_item_flag=1

        if Have_same_item_flag == 0:
            return False
        else:
            new_clause = (set1 | set2 )
        if len(new_clause)==0:
            return False
        else:
            return list(new_clause)

    


a, b, c, d = symbols('a b c d')
bb = BeliefBase()

# clause1 = [a, -c]
# clause2 = [a]
# print(bb.resolve(clause1, clause2))

bb.addBelief("(a iff c) or b")
bb.addBelief("(a)")
print(bb.getBeliefSet())

#print(bb.checkForContradiction([[a, b]]))
#beliefs = [[-c, b, a], [-a, b, c], [b], [a]]
# b = BeliefBase()
# beliefs = b.negateBelief(beliefs)
# print(beliefs)

#string = "(a iff c) or b"
# string = "(neg a or b or c) and (neg b or a) and (neg c or a) and (neg a)"
# string2 = "(neg b)"
# b = BeliefBase()

# b.addBelief(string)
# b.addBelief(string2)
# print(b.getBeliefSet())