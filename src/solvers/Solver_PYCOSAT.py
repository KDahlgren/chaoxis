# modified from https://github.com/palvaro/ldfi-py

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import pycosat
from types import *
import inspect, os, sys, time

import SATVars_PYCOSAT

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# **************************************** #



##########################
#  CLASS SOLVER PYCOSAT  #
##########################
class Solver_PYCOSAT :


  ################
  #  ATTRIBUTES  #
  ################
  fmlaVars   = None
  satformula = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__(self, cnf):

    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT()
    self.satformula = []

    # assign integer ids to variables per disjunctive clause:
    for clause in cnf.getConjuncts() :
      satclause = map( self.fmlaVars.lookupVar, clause )
      self.satformula.append( list(satclause ) )


  ###############
  #  SOLUTIONS  #
  ###############
  def solutions(self):
    for soln in pycosat.itersolve(self.satformula):
        yield map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln))


  ##############
  #  CONTAINS  #
  ##############
  def contains(self, large, small):
    for item in small:
      if not item in large:
        return False
    return True


  #######################
  #  CONTAINED_IN_NONE  #
  #######################
  def contained_in_none(self, done, soln):
    for item in done:
      if self.contains(soln, item):
        return False
    return True


  #######################
  #  MINIMAL_SOLUTIONS  #
  #######################
  #
  # (Alvaro, P. :)
  # this is a bit of a strawman.  the idea is, we need to enumerate all of the SAT
  # solutions to know which is the smallest!  the containment thing in the old version (below)
  # seems sketchy to me, due to nonmonotonicity.  return to this later.
  #
  def minimal_solutions( self ) :

    solns = []
    print "self.satformula = " + str( self.satformula )

    for soln in pycosat.itersolve( self.satformula ) :
      solns.append( frozenset( map( self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln) ) ) )

    for soln in sorted( solns, key=self.getKey ) :
      yield soln


  #########################
  #  N MINIMAL_SOLUTIONS  #
  #########################
  def Nminimal_solutions(self):
    solns = []        
    done = []
    for soln in pycosat.itersolve(self.satformula):
      solns.append(frozenset(map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln))))

    for soln in sorted(solns, key=self.getKey):
      #if not done.has_key(soln):
      #    yield soln
      if self.contained_in_none(done, soln):
        yield soln
      done.append(soln)


  #############
  #  GET KEY  #
  #############
  def getKey(self, item) :
    return len( item )


#########
#  EOF  #
#########
