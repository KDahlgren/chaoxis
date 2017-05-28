# modified from https://github.com/palvaro/ldfi-py

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import pycosat
from types import *
import inspect, itertools, os, sys, time

import SATVars_PYCOSAT

# ------------------------------------------------------ #
# import sibling packages HERE!!!

import solverTools

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# **************************************** #

DEBUG = False

##########################
#  CLASS SOLVER PYCOSAT  #
##########################
class Solver_PYCOSAT :


  ################
  #  ATTRIBUTES  #
  ################
  fmlaVars        = None
  satformula      = None
  numsolns        = None
  currSolnAttempt = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, cnf_str, fault_id ):

    self.currSolnAttempt = fault_id

    #tools.bp( __name__, inspect.stack()[0][3], "cnf_str = " + cnf_str )

    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT()
    self.satformula = []

    if DEBUG :
      print "----------------------"
      print " solverTools.getConjuncts( cnf_str ) = "
      print solverTools.getConjuncts( cnf_str )
      print "----------------------"

    # assign integer ids to variables per disjunctive clause:
    for clause in solverTools.getConjuncts( cnf_str ) :

      satclause = map( self.fmlaVars.lookupVar, clause )
      satclause = [ var for var in satclause if var ] # remove 'None' variables from satclause
      #
      # ^justification:
      # Only combinations of clock deletions are interesting.
      # Removing non-clock facts from CNF clause is equivalent to relegating the value to False.
      # By defn, False OR p == p.
      # Therefore, removing the non-clock facts does not affect the outcome, if we're only
      # interested in the impact of T/F assignments to clock fact variables.

      if not satclause == [] :
        self.satformula.append( list(satclause) )

      if DEBUG :
        print "clause     = " + str(clause)
        print "satclause  = " + str(satclause)
        print "satformula = " + str(self.satformula)
        print "map( self.fmlaVars.lookupVar, clause ) = " + str(map( self.fmlaVars.lookupVar, clause ))

    #tools.bp( __name__, inspect.stack()[0][3], "self.satformula = " + str(self.satformula) )


  ###################
  #  ALL SOLUTIONS  #
  ###################
  # calculate and return all solutions to the cnf formula associated with this instance.
  def allSolutions( self ) :

    if DEBUG :
      print "solutions: self.satformula = " + str( self.satformula )

    # DEVELOPER's NOTE: calculating numsolns is _VERY_ SLOW. only run on small examples. 
    # self.numsolns = len( list( pycosat.itersolve( self.satformula ) ) )
    # print "self.numsolns = " + str(self.numsolns) 

    if DEBUG :
      print "running itersolve( self.satformula) in for loop..."

    for soln in pycosat.itersolve( self.satformula ) :

      if DEBUG :
        print "saving soln = " + str(soln)

      yield frozenset( map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln)) ) # using yield because soln set could be huge
      #return map(self.fmlaVars.lookupNum, filter(lambda x: x > 0, soln)) # not using yield because generators are a headache and a half.


  ######################
  #  ONE NEW SOLUTION  #
  ######################
  # input list of previously tried solutions.
  # calculate and return a solution to the cnf formula associated with this instance
  # such that the solution is not among the list of previously tried solutions.
  #def oneNewSolution( self, oldSolutions ) :
  def oneNewSolution( self ) :

    if DEBUG :
      print "solutions: self.satformula = " + str( self.satformula )

    # grab all solns up to currSolnAttempt. returns a list. the largest element will be new.
    solnList = list( itertools.islice( pycosat.itersolve( self.satformula ), self.currSolnAttempt ) )

    print "self.currSolnAttempt = " + str( self.currSolnAttempt )
    print "solnList  = " + str(solnList)

    if DEBUG :
      print "self.currSolnAttempt = " + str( self.currSolnAttempt )
      print "solnList  = " + str(solnList)
      #print "map( self.fmlaVars.lookupNum, solnList[0]) = " + str(map( self.fmlaVars.lookupNum, solnList[0]))

    #print "solnList[-1]                                  = " + str( solnList[-1] )
    #print "map(self.fmlaVars.lookupNum, solnList[:-1]) ) = " + str( map(self.fmlaVars.lookupNum, solnList[-1]) )
    #print "frozenset                                     = "  + str( frozenset( map( self.fmlaVars.lookupNum, solnList[-1]) ) ) # new solns are added to the end.

    return frozenset( map( self.fmlaVars.lookupNum, solnList[-1]) ) # new solns are added to the end.


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
