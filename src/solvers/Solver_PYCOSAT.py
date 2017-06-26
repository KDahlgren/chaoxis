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
  prevSolnAttempt = 0
  currSolnAttempt = 1
  initFmla        = None  # the formula for the initial good execution.
  prevLastSoln    = None  # maintain the previous last soln. 
                          # if current last soln == prev last soln, 
                          # then no new solutions exist.

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
    self.fmlaVars   = SATVars_PYCOSAT.SATVars_PYCOSAT( )
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

    # grab a new soln
    soln = self.getSoln()

    # convert soln into a trigger fault
    triggerFault = self.convertToTrigger( soln )

    return triggerFault


  ###############################
  #  SET OF NEW TRIGGER FAULTS  #
  ###############################
  def setOfNewTriggerFaults( self, buffersize ) :

    # grab a set of new solutions
    solnSet = self.getSolnSet( buffersize )
 
    # convert solutions into trigger faults
    triggerFaultSet = []
    for aSoln in solnSet :
      triggerFaultSet.append( self.convertToTrigger( aSoln ) )

    return triggerFaultSet


  ##############
  #  GET SOLN  #
  ##############
  def getSoln( self ) :

    # grab all solns up to currSolnAttempt. returns a list of size == currSolnAttempt. the largest element will be new.
    solnList = list( itertools.islice( pycosat.itersolve( self.satformula ), self.currSolnAttempt ) )
    self.currSolnAttempt += 1

    if DEBUG :
      print "self.currSolnAttempt = " + str( self.currSolnAttempt )
      print "solnList  = " + str(solnList)

    # grab a new soln from the solver
    aSoln = frozenset( map( self.fmlaVars.lookupNum, solnList[-1]) ) # new solns are added to the end.
    aSoln = self.getLegibleSoln( aSoln ) 

    return aSoln


  ##################
  #  GET SOLN SET  #
  ##################
  # grab a new set of solutions of size = buffersize
  def getSolnSet( self, buffersize ) :

    # set currSolnAttempt to buffersize
    self.currSolnAttempt = buffersize

    print "========================================================="
    print "self.prevSolnAttempt = " + str( self.prevSolnAttempt )
    print "self.currSolnAttempt = " + str( self.currSolnAttempt )

    # grab all solns up to currSolnAttempt. returns a list of size currSolnAttempt. the new soln set is prevSolnAttempt through currSolnAttempt-1
    fullSolnList          = list( itertools.islice( pycosat.itersolve( self.satformula ), self.currSolnAttempt ) )
    solnSet               = fullSolnList[ self.prevSolnAttempt : self.currSolnAttempt ]
    self.prevSolnAttempt  = self.currSolnAttempt
    self.currSolnAttempt += buffersize

    print "fullSolnList         = " + str( fullSolnList         )
    print "solnSet              = " + str( solnSet              )

    if DEBUG :
      print "self.prevSolnAttempt = " + str( self.prevSolnAttempt )
      print "self.currSolnAttempt = " + str( self.currSolnAttempt )
      print "solnSet              = " + str( solnSet              )

    # make solutions legible
    legibleSolnSet = []
    for aSoln in solnSet :
      aSoln = frozenset( map( self.fmlaVars.lookupNum, aSoln ) ) # new solns are added to the end.
      aSoln = self.getLegibleSoln( aSoln )
      legibleSolnSet.append( aSoln )

    print ">> legible soln set = " + str( legibleSolnSet )

    # pycosat will return the same list if currSolnAttempt exceeds 
    # maximum number of unique solutions.
    # break if last element of new soln list is identical to the last
    # element of the previous soln list.
    if fullSolnList[-1] == self.prevLastSoln :
      #tools.bp( __name__, inspect.stack()[0][3], "no new solns!" )
      return []

    # otherwise, new solutions exist.
    else :
      print
      print fullSolnList[-1]
      print self.prevLastSoln
      print
      self.prevLastSoln = fullSolnList[-1] # reset previous last soln

      return legibleSolnSet


  #############################
  #  GET CLOCK FACT CONTENTS  #
  #############################
  def getClockFactContents( self, fact ) :
    # isolate the first and second components of the clock fact
    tup = fact.split( "([" )
    tup = tup[-1]
    tup = tup.replace( "])", "" )
    tup = tup.split( "," ) # the complete tuple as an array [ src, dest, sndTime, delivTime ]
    return tup


  ######################
  #  GET LEGIBLE SOLN  #
  ######################
  # given messy raw solution
  # output legible version
  def getLegibleSoln( self, aSoln ) :

    fmlaStr = []  # stores the legible version of the soln.

    # make legible
    for var in aSoln :
      fmlaStr.append( solverTools.toggle_format_str( var, "legible" ) )

    return fmlaStr


  ########################
  #  CONVERT TO TRIGGER  #
  ########################
  # positive clock facts imply the execution was good because the facts DID NOT happen.
  # handling these is future work.
  def convertToTrigger( self, soln ) :

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
