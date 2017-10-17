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

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from core      import LDFICore
from utilities import tools
from solvers   import solverTools

# **************************************** #


DEBUG = tools.getConfig( "FAULTMANAGER", "FAULTMANAGER_DEBUG", bool )


class FaultManager :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  # files saving data dump and intermediate file locations
  argDict = None # dictionary of command line arguments
  cursor  = None # reference to the IR database

  # the instance of LDFICore
  core = None

  # the index of the cnf fmla in core to examine in this iteration
  fmla_index = 0

  # transient data ( change per iteration of run() )
  conclusion   = None  # bug conclusion = None / FoundCounterexample / NoCounterexampleFound
  triggerFault = None  # the fault to inject in the next iteration
  noNewSolns   = None  # a boolean for controlling the infinite loop over the LDFI core.
  currFmla     = None  # string or None.

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, argDict, cursor ) :

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
  def run( self ) :

    while True :
      if DEBUG :
        print "============================================="
        print "            FAULT MANAGER RUN()"
        print "============================================="

      # run LDFI workflow and gather results
      # results := [ conclusion/None, noNewSolns/None, triggerFault/None ]
      results = self.core.run_workflow( self.triggerFault, self.fmla_index )

      # collect old fault for records
      oldTriggerFault = self.triggerFault

      # grab data from run
      # provTree_fmla       is not None iff no conclusion exists.
      # likewise, solution  is not None iff no conclusion exists.
      self.conclusion   = results[0]
      self.explanation  = results[1]
      self.triggerFault = results[2]
      self.noNewSolns   = results[3]
      self.currFmla     = results[4]

      # display results
      print
      print "**************************************************************"
      print "* ::: RESULTS :::"
      print "* FAULT MANAGER RUN() on fault_id    : " + str( self.core.fault_id )
      print "* self.fmla_index                    : " + str( self.fmla_index    )
      print "* self.conclusion                    : " + str( self.conclusion    )
      print "* self.explanation                   : " + str( self.explanation   )
      print "* self.noNewSolns                    : " + str( self.noNewSolns    )
      print "* COMPLETED run_workflow() for fault : " + str( oldTriggerFault    )
      if not self.noNewSolns :
        print "* NEXT trigger fault                 : " + str( self.triggerFault  )
        print
      if self.core.initFmla_list and self.fmla_index < len( self.core.initFmla_list ) - 1 :
        #self.core.fault_id += 1 
        print "* NEXT fmla : "
        print str( self.core.initFmla_list[ self.fmla_index + 1 ] )
      else :
        print "* currFmla :"
        print self.currFmla
      print "**************************************************************"
      print

      # CASE : found a counter example
      if self.conclusion == "FoundCounterexample" :
        break

      else :
        # CASE : fmla suggested by spec is not satisfiable. therefore, protocol is correct.
        if ( oldTriggerFault == None and self.triggerFault == None ) or self.noNewSolns :
          # CASE : specification invalid after first iteration w/o injecting faults.
          if not self.core.initFmla_list :
            break
          if self.fmla_index == len( self.core.initFmla_list ) - 1 :
            print "* Final Conclusion : input specification is PyLDFI-certified."
            print
            print "**************************************************************"
            print
            break
          else :
            self.fmla_index += 1

        # break infinite execution if no new solutions exist.
        elif self.noNewSolns :
          if self.fmla_index == len( self.core.initFmla_list ) - 1 :
            break
          else :
            self.fmla_index += 1

        # check if still bug free
        elif not self.isBugFree() :
          if self.fmla_index == len( self.core.initFmla_list ) - 1 :
            break
          else :
            self.fmla_index += 1


  #################
  #  IS BUG FREE  #
  #################
  def isBugFree( self ) :

    ###############
    #  BASE CASE  #
    ###############
    # branch on cases
    # CASE 1 : if FoundCounterexample, then return immediately.
    # CASE 2 : if NoCounterexampleFound, then return conclusion. program is bug free.

    # CASE 1 : if conclusion is FoundCounterExample, then return conclusion immediately.
    if self.conclusion == "FoundCounterexample" :
      return False

    ####################
    #  RECURSIVE CASE  #
    ####################
    # otherwise, have not hit a conclusion yet
    # RECURSIVE CASE : NoCounterexampleFound, so find a new soln and try again.
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
