class BeliefBase:
    def __init__(self) -> None:
        self.beliefBase = set()
    def addBelief(self,belief):
        self.beliefBase.add(belief)
    def removeBelief(self,belief):
        if belief in self.beliefBase:
            self.beliefBase.remove(belief)
    def getbeliefSet(self):
        print(self.beliefBase)
