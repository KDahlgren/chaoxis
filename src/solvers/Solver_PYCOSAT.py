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


DEBUG = tools.getConfig( "SOLVERS", "SOLVER_PYCOSAT_DEBUG", bool )


##########################
#  CLASS SOLVER PYCOSAT  #
##########################
class Solver_PYCOSAT :

  ################
  #  ATTRIBUTES  #
  ################
  fmlaVars        = None
  satformula      = None
  currSolnAttempt = 1
  initFmla        = None  # the formula for the initial good execution.


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, initFmla ) :
    pass


  ##############
  #  SET FMLA  #
  ##############
  def setFmla( self, cnf_str ) :

    # set current fmla
    self.initFmla   = cnf_str
    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT()
    self.satformula = []

    if DEBUG :
      print "----------------------------------------------------"
      print " solverTools.getConjuncts( self.initFmla ) = "
      print solverTools.getConjuncts( self.initFmla )
      print "----------------------------------------------------"

    # assign integer ids to variables per disjunctive clause:
    for clause in solverTools.getConjuncts( self.initFmla ) :

      satclause = map( self.fmlaVars.lookupVar, clause )
      satclause = [ var for var in satclause if var ] # remove 'None' variables from satclause
      #
      # ^justification:
      # Only certain combinations of clock deletions are interesting.
      # Removing non-clock facts from CNF clause is equivalent to relegating the value to False.
      # By defn, (False OR p) == p.
      # Therefore, removing facts such as non-clocks and self-comms does not affect the outcome, if we're only
      # interested in the impact of T/F assignments to interesting clock fact variables.

      if not satclause == [] :
        self.satformula.append( list(satclause) )

      if DEBUG :
        print "clause     = " + str(clause)
        print "satclause  = " + str(satclause)
        print "satformula = " + str(self.satformula)
        print "map( self.fmlaVars.lookupVar, clause ) = " + str(map( self.fmlaVars.lookupVar, clause ))


  ###################
  #  ALL SOLUTIONS  #
  ###################
  # calculate and return all solutions to the cnf formula associated with this instance.
  def allSolutions( self ) :

    if DEBUG :
      print "solutions: self.satformula = " + str( self.satformula )

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
    soln = self.getSoln()

    # convert soln into a trigger fault
    triggerFault = self.getTrigger( soln )

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

    return triggerFault


#########
#  EOF  #
#########
