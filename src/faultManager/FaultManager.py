#!/usr/bin/env python

'''
FaultManager.py
  A long-lived tree data structure responsible for maintining
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

import ConclusionTypes

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from core           import LDFICore
from utils          import tools

# **************************************** #

DEBUG = True

class FaultManager :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  # files saving data dump and intermediate file locations
  c4_dump_savepath  = None
  table_list_path   = None
  datalog_prog_path = None
  argDict           = None # dictionary of command line arguments
  cursor            = None # reference to the IR database

  # the instance of LDFICore
  core = None

  # runtime data
  # transient data (change per iteration of run())
  provTree_merged = None  # the current vision of the prov tree monotonically augmented over all runs.
  old_faults      = []    # the list of previously tried faults
  old_solutions   = []    # the list of previously tried solutions
  triggerFault    = None  # the current fault to inject
  solution        = []    # generated after running LDFI with the chosen trigger fault
  fault_id        = 1     # integers starting at 1
  conclusion      = None  # bug conclusion = None / FoundCounterexample / NoCounterexampleFound

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, c4_save, table_save, datalog_save, argDict, cursor ) :

    # file paths + execution configs (do not change per execution of PyLDFI)
    self.c4_dump_savepath  = c4_save
    self.table_list_path   = table_save
    self.datalog_prog_path = datalog_save
    self.argDict           = argDict
    self.cursor            = cursor

    # instantiate LDFICore
    self.core = LDFICore.LDFICore( self.c4_dump_savepath, self.table_list_path, self.datalog_prog_path, self.argDict, self.cursor )


  #########
  #  RUN  #
  #########
  # run the LDFI core on this trigger fault
  # LDFICore returns [ conclusion/None, cnf_formula/None, solution/None ]
  # solution := solution to the cnf_formula
  # returns a conclusion string
  def run( self ) :

    if DEBUG :
      print "============================================="
      print "            FAULT MANAGER RUN()"
      print "============================================="
      print "    fault_id      = " + str( self.fault_id )
      print "    triggerFault  = " + str( self.triggerFault )
      print "    old_faults    = " + str( self.old_faults )
      print "    old_solutions = " + str( self.old_solutions )

    # run LDFI workflow and gather results
    # results := [ conclusion/None, provTree_merged/None, solution/None ]
    results = self.core.run_workflow( self.triggerFault, self.provTree_merged, self.old_faults )

    # grab data from run
    # provTree_merged     is not None iff no conclusion exists.
    # likewise, solution  is not None iff no conclusion exists.
    self.conclusion      = results[0]
    self.provTree_merged = results[1]
    self.solution        = results[2]

    if DEBUG :
      print "self.conclusion      = "       + str( self.conclusion      )
      print "self.provTree_merged = "       + str( self.provTree_merged )
      print "self.solution        = "       + str( self.solution        )
      print "COMPLETED run_workflow() for " + str( self.triggerFault    )


    ###############
    #  BASE CASE  #
    ###############
    # branch on cases
    # CASE 1 : if FoundCounterExample, then return immediately.
    # CASE 2 : if NoCounterexampleFound and no new solutions, then return conclusion. program is bug free.

    # CASE 1 : if conclusion is FoundCounterExample, then return conclusion immediately.
    if self.conclusion == "FoundCounterexample" :
      print "returning counterexample info..."
      return self.conclusion

    # CASE 2 : if conclusion is NoCounterexampleFound, then return conclusion immediately. ( TEMPORARY )
    elif self.conclusion == "NoCounterexampleFound" and self.getTrigger( self.solution ) in self.old_faults :
      print "BREAK CONDITION --> self.getTrigger( self.solution ) in self.old_faults"
      print "returning result info..."
      return self.conclusion


    ####################
    #  RECURSIVE CASE  #
    ####################
    # otherwise, have not hit a conclusion yet
    # RECURSIVE CASE : if NoCounterexampleFound and new solutions exist, then find a new soln and try again.
    else :
      if DEBUG :
        print str( self.triggerFault ) + " : self.conclusion  = " + str( self.conclusion )
        print str( self.triggerFault ) + " : self.solution   = " + str( self.solution )

      # add evaluated triggerFault to old_faults
      self.old_faults.append( self.triggerFault )

      # recurse until counterexample found or run out of new solutions
      self.triggerFault = self.getTrigger( self.solution ) # clean solution into a trigger fault

      # increment the fault id
      self.core.fault_id += 1

      self.run()


  #################
  #  GET TRIGGER  #
  #################
  # positive clock facts imply the execution was good because the facts DID NOT happen.
  # handling these is future work.
  def getTrigger( self, soln ) :

    triggerFault = []
    for literal in soln :
      if "NOT" in literal :                 # do not include positive clock facts
        triggerFault.append( literal[4:] )  # strip off the NOT

    return triggerFault


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return str( self.fault_id ) + " : " + str( self.triggerFault )



#########
#  EOF  #
#########
