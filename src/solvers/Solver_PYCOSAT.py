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

from utils   import tools
from solvers import newProgGenerationTools
# **************************************** #

DEBUG = True

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

  currSolnAttempt = 1
  noNewSolns      = False
  old_faults      = []
  prev_fmla       = None
  prev_soln       = None
  curr_fmla       = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self ) :
    pass


  ##############
  #  SET FMLA  #
  ##############
  def setFmla( self, cnf_str ) :

    # set current fmla
    self.curr_fmla = cnf_str

    # combine fmlas if applicable
    if self.prev_fmla and not self.prev_fmla == self.curr_fmla :
      #self.curr_fmla       = "(" + self.curr_fmla + ") OR " + self.prev_fmla # merge fmlas
      self.curr_fmla       = self.curr_fmla + " OR " + self.prev_fmla # merge fmlas
      self.currSolnAttempt = 1 # need to reset b/c new fmla
      #tools.bp( __name__, inspect.stack()[0][3], "self.curr_fmla = " + self.curr_fmla + "\nself.prev_fmla = " + str(self.prev_fmla) )

    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT()
    self.satformula = []

    if DEBUG :
      print "----------------------"
      print " solverTools.getConjuncts( self.curr_fmla ) = "
      print solverTools.getConjuncts( self.curr_fmla )
      print "----------------------"

    # assign integer ids to variables per disjunctive clause:
    for clause in solverTools.getConjuncts( self.curr_fmla ) :

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

    # save curr fmla as prev fmla
    if self.curr_fmla :
      self.prev_fmla = self.curr_fmla



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
  def oneNewTriggerFault( self ) :

    if DEBUG :
      print "solutions: self.satformula = " + str( self.satformula )

    # grab an initial soln
    soln = self.getSoln( )

    # convert soln into a trigger fault
    triggerFault = self.getTrigger( soln )

    # check if trigger fault is new. if not, grab the next soln
    while triggerFault in self.old_faults :
      soln                  = self.getSoln()
      triggerFault          = self.getTrigger( soln )

      if triggerFault in self.old_faults :
        print "already tried : "  + str( triggerFault )

      if self.noNewSolns :
        break

    # add new fault to old_faults
    self.old_faults.append( triggerFault )

    #triggerFault = ['clock([a,b,1,2])', 'clock([a,_,2,_])'] # rdlog correct
    #triggerFault = ['clock([a,b,1,2])']                     # simplog

    #triggerFault = ['clock([a,a,2,3])', 'clock([a,c,2,3])', 'clock([a,b,1,2])', 'clock([a,b,2,3])']
    #triggerFault = ['clock([a,c,2,3])', 'clock([a,c,1,2])', 'clock([a,b,1,2])', 'clock([a,c,3,4])', 'clock([a,b,2,3])']

    return triggerFault


  ##############
  #  GET SOLN  #
  ##############
  def getSoln( self ) :

    # grab all solns up to currSolnAttempt. returns a list. the largest element will be new.
    solnList = list( itertools.islice( pycosat.itersolve( self.satformula ), self.currSolnAttempt ) )
    self.currSolnAttempt += 1

    if DEBUG :
      print "self.currSolnAttempt = " + str( self.currSolnAttempt )
      print "solnList  = " + str(solnList)

    # grab a new soln from the solver
    aSoln = frozenset( map( self.fmlaVars.lookupNum, solnList[-1]) ) # new solns are added to the end.
    aSoln = self.getLegibleFmla( aSoln ) 

    # check if the new soln is identical to the previous soln
    if aSoln == self.prev_soln :
      self.noNewSolns = True

    return aSoln


  ######################
  #  GET LEGIBLE FMLA  #
  ######################
  # given messy raw solution
  # output legible version
  def getLegibleFmla( self, aSoln ) :

    fmlaStr = []  # stores the legible version of the soln.

    # make legible
    for var in aSoln :
      fmlaStr.append( solverTools.toggle_format_str( var, "legible" ) )

    return fmlaStr


  #################
  #  GET TRIGGER  #
  #################
  # positive clock facts imply the execution was good because the facts DID NOT happen.
  # handling these is future work.
  def getTrigger( self, soln ) :

    if DEBUG :
      print "IN GETTRIGGER()"

    triggerFault = []
    for literal in soln :

      if DEBUG :
        print "* literal = " + str( literal )

      if "clock(" in literal :                # trigger faults contain only clock facts
        if "NOT" in literal :                 # do not include positive clock facts
          triggerFault.append( literal[4:] )  # strip off the NOT

    if DEBUG :
      triggerFault = self.removeCrashes( triggerFault ) # debugging only
      triggerFault = self.removeSelfComms( triggerFault )

    return triggerFault


  #######################
  #  REMOVE SELF COMMS  #
  #######################
  # input a solution consisting only of clock facts.
  # outputs a list of containing solutions such that each solution contains 
  # the original set of clock facts, minus the self-comm clock facts ( e.g. clock('a','a',1,2) )
  def removeSelfComms( self, soln ) :

    if DEBUG :
      print "IN REMOVESELFCOMMS"
      print ">soln = " + str( soln )

    cleanSoln = []
    for clockFact in soln :

      if DEBUG :
        print "clockFact = " + str(clockFact)

      content = newProgGenerationTools.getContents( clockFact )
      content = content.split( "," )
      if content[0] == content[1] : # sender is the same as the receiver
        pass
      else :
        cleanSoln.append( clockFact )

    if DEBUG :
      print "cleanSoln = " + str( cleanSoln )

    return cleanSoln


  ####################
  #  REMOVE CRASHES  #
  ####################
  # input a soln consisting only of clock facts.
  # outputs a list of containing solutions such that each solution contains 
  # the original set of clock facts, minus the clock facts indicating crash failures( e.g. clock('a','_',1,_) )
  def removeCrashes( self, soln ) :

    cleanSoln = []
    for clockFact in soln :
      content = newProgGenerationTools.getContents( clockFact )
      content = content.split( "," )
      if content[1] == "_" : # sender is the same as the receiver
        pass
      else :
        cleanSoln.append( clockFact )

    return cleanSoln


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
