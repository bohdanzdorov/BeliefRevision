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

beliefOb1 = BeliefBase()
beliefOb1.addBelief("q and r")
beliefOb1.addBelief("x and a")
beliefOb1.addBelief("x or y")
beliefOb1.removeBelief("x or y")
beliefOb1.addBelief("x1 and y")
beliefOb1.addBelief("x1 and y")

beliefOb1.getbeliefSet()