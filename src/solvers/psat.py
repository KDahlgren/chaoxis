# modified from https://github.com/palvaro/ldfi-py

import pycosat
from types import *

class SATVars:
  def __init__(self):
    self.var2num = {}
    self.num2var = {}
    self.counter = 1

  def lookupVar(self, var):
    print "var = " + str( var )

    # case var is list
    if type( var ) is list :
      for l in var :
        return self.lookupVar( l )

    # base case
    else :
      if not self.var2num.has_key(var):
        self.var2num[var] = self.counter
        self.num2var[self.counter] = var
        self.counter += 1

      return self.var2num[var]

  def lookupNum(self, num):
    if num < 0:
      return "NOT " + self.num2var[-num]
    else:
      return self.num2var[num]


class Solver:
    def __init__(self, cnf):

        self.vars = SATVars()
        self.satformula = []
        #for clause in cnf.conjuncts():
        for clause in cnf.getConjuncts():
            satclause = map(self.vars.lookupVar, clause)
            self.satformula.append(list(satclause))

    def solutions(self):
        for soln in pycosat.itersolve(self.satformula):
            yield map(self.vars.lookupNum, filter(lambda x: x > 0, soln))

    def contains(self, large, small):
        for item in small:
            if not item in large:
                return False
        return True

    def contained_in_none(self, done, soln):
        for item in done:
            if self.contains(soln, item):
                return False
        return True
    
    def minimal_solutions(self):
        # this is a bit of a strawman.  the idea is, we need to enumerate all of the SAT
        # solutions to know which is the smallest!  the containment thing in the old version (below)
        # seems sketchy to me, due to nonmonotonicity.  return to this later.
        solns = []
        for soln in pycosat.itersolve(self.satformula):
            solns.append(frozenset(map(self.vars.lookupNum, filter(lambda x: x > 0, soln))))

        def getKey(item):
            return len(item)

        for soln in sorted(solns, key=getKey):
            yield soln
    
    def Nminimal_solutions(self):
        solns = []        
        done = []
        for soln in pycosat.itersolve(self.satformula):
            solns.append(frozenset(map(self.vars.lookupNum, filter(lambda x: x > 0, soln))))
        
        def getKey(item):
            return len(item)

        for soln in sorted(solns, key=getKey):
            #if not done.has_key(soln):
            #    yield soln
            if self.contained_in_none(done, soln):
                yield soln
            done.append(soln)


#########
#  EOF  #
#########
