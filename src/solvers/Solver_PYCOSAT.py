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

import solverTools

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
  numsolns   = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__(self, cnf_str):

    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT()
    self.satformula = []

    # assign integer ids to variables per disjunctive clause:
    for clause in solverTools.getConjuncts( cnf_str ) :
      satclause = map( self.fmlaVars.lookupVar, clause )
      self.satformula.append( list(satclause ) )


  ###############
  #  SOLUTIONS  #
  ###############
  def solutions( self ) :
    print "solutions: self.satformula = " + str( self.satformula )
    print "len( pycosat.itersolve( self.satformula ) ) = " + str( len( list( pycosat.itersolve( self.satformula ) ) ) )

    self.numsolns = len( list( pycosat.itersolve( self.satformula ) ) )

    for soln in pycosat.itersolve( self.satformula ) :
        yield frozenset( map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln)) ) # using yield because soln set could be huge
        #return map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln)) # not using yield because generators are a headache and a half.


  ##############
  #  CONTAINS  #
  ##############
  def contains( self, large, small ) :

    for item in small:
      if not item in large:
        return False

    return True


  #######################
  #  CONTAINED_IN_NONE  #
  #######################
  def contained_in_none( self, done, soln ) :

    for item in done:
      if self.contains(soln, item):
        return False

    return True


  #######################
  #  MINIMAL_SOLUTIONS  #
  #######################
  #
  # Alvaro, P. :
  # this is a bit of a strawman.  the idea is, we need to enumerate all of the SAT
  # solutions to know which is the smallest!  the containment thing in the old version (below)
  # seems sketchy to me, due to nonmonotonicity.  return to this later.
  #
  def minimal_solutions( self ) :
    print "minimal_solutions: self.satformula = " + str( self.satformula )

    solns = []
    for soln in pycosat.itersolve( self.satformula ) :
      res = frozenset( map( self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln) ) )
      solns.append( res )

    #tools.bp( __name__, inspect.stack()[0][3], "sorted( solns, key=self.getLen ) = " + str( sorted( solns, key=self.getLen ) ) )

    minSolnLen       = 0
    solnsSortedByLen = sorted( solns, key=self.getLen )
    minSolns         = []
    for i in range(0,len(solnsSortedByLen)) :
      soln = solnsSortedByLen[i]

      # skip empty solutions
      if len( soln ) == 0 :
        pass

      # set the min soln length
      elif minSolnLen == 0 :
        minSolnLen = len(soln)
        minSolns.append( list( soln ) ) # cast from frozenset to list as a remedy for migraines

      # collect the min solution set
      elif len(soln) == minSolnLen :
        minSolns.append( list( soln ) ) # cast from frozenset to list as a remedy for migraines

      # break if hit a longer soln
      if len(soln) > minSolnLen :
        break

    yield minSolns  # using yield because soln set could be massive
    #return minSolns  # not using yield because generators are a headache and a half.


  #########################
  #  N MINIMAL_SOLUTIONS  #
  #########################
  # broken + questionable existence?
  def Nminimal_solutions( self ) :
    print "Nminimal_solutions: self.satformula = " + str( self.satformula )

    solns = []        
    done = []

    # ------------------------------------------------ #
    for soln in pycosat.itersolve( self.satformula ) :
      res = frozenset( map( self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln) ) )
      solns.append( res )

    # ------------------------------------------------ #
    for soln in sorted( solns, key=self.getLen ) :

      if self.contained_in_none( done, soln ) :
        yield soln # using yield because soln set could be massive

      done.append( soln )


  ############
  #  GET LEN #
  ############
  def getLen( self, item ) :
    return len( item )


#########
#  EOF  #
#########
