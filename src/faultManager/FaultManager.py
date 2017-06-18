#!/usr/bin/env python

'''
FaultManager.py
  A long-lived tree data structure responsible for managing
  the fault hypotheses encountered over the course of a 
  series of injections.
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from core    import LDFICore
from utils   import tools, settings
from solvers import solverTools

# **************************************** #


DEBUG = tools.getConfig( "FaultManager", "DEBUG", bool )


class FaultManager :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  # files saving data dump and intermediate file locations
  argDict           = None # dictionary of command line arguments
  cursor            = None # reference to the IR database

  # the instance of LDFICore
  core = None

  # runtime data
  # transient data (change per iteration of run())
  conclusion    = None  # bug conclusion = None / FoundCounterexample / NoCounterexampleFound
  noNewSolns    = False # bool indicating whether more new solutions exist
  triggerFault  = None  # the current fault to inject
  provTree_fmla = None

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, argDict, cursor ) :

    # set settings
    settings.settings( argDict[ "settings" ] )

    # set run data and database
    self.argDict           = argDict
    self.cursor            = cursor

    # create a Solver_PYCOSAT insance
    solver = solverTools.solveCNF( "PYCOSAT" )

    # instantiate LDFICore
    self.core = LDFICore.LDFICore( self.argDict, self.cursor, solver )


  #########
  #  RUN  #
  #########
  # run the LDFI core on this trigger fault
  # LDFICore returns [ conclusion/None, cnf_formula/None, solution/None ]
  # solution := solution to the cnf_formula
  # returns a conclusion string
  def run( self ) :

    while True :
      if DEBUG :
        print "============================================="
        print "            FAULT MANAGER RUN()"
        print "============================================="

      # run LDFI workflow and gather results
      # results := [ conclusion/None, noNewSolns/None, triggerFault/None ]
      results = self.core.run_workflow( self.triggerFault, self.provTree_fmla )

      # grab data from run
      # provTree_fmla       is not None iff no conclusion exists.
      # likewise, solution  is not None iff no conclusion exists.
      self.conclusion    = results[0]
      self.provTree_fmla = results[1]
      self.triggerFault  = results[2]
      self.noNewSolns    = results[3]

      if DEBUG :
        print "self.provTree_fmla = " + str( self.provTree_fmla )
        print

      # display results
      print
      print "**************************************************************"
      print "* FAULT MANAGER RUN() : fault_id = " + str( self.core.fault_id )
      print "* self.conclusion   = "              + str( self.conclusion    )
      print "* self.noNewSolns   = "              + str( self.noNewSolns    )
      print "* COMPLETED run_workflow() for "     + str( self.triggerFault  )
      print "**************************************************************"

      # check if still bug free
      if not self.isBugFree() :
        break


  #################
  #  IS BUG FREE  #
  #################
  def isBugFree( self ) :

    ###############
    #  BASE CASE  #
    ###############
    # branch on cases
    # CASE 1 : if FoundCounterexample, then return immediately.
    # CASE 2 : if NoCounterexampleFound and no new solutions, then return conclusion. program is bug free.

    # CASE 1 : if conclusion is FoundCounterExample, then return conclusion immediately.
    if self.conclusion == "FoundCounterexample" :
      print "display counterexample info..."
      return False

    # CASE 2 : if conclusion is NoCounterexampleFound and no new solutions
    elif self.conclusion == "NoCounterexampleFound" and self.noNewSolns :
      print "display result info..."
      return False


    ####################
    #  RECURSIVE CASE  #
    ####################
    # otherwise, have not hit a conclusion yet
    # RECURSIVE CASE : if NoCounterexampleFound and new solutions exist, then find a new soln and try again.
    else :

      if DEBUG :
        print "triggerFault for next run_workflow  = " + str( self.triggerFault )

      # increment the fault id
      self.core.fault_id += 1

      # loop until counterexample found or run out of new solutions
      return True


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return str( self.core.fault_id ) + " : " + str( self.triggerFault )



#########
#  EOF  #
#########
