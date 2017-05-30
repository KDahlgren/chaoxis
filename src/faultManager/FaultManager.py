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
  provTree_fmla = None  # the current vision of the prov tree fmla monotonically augmented over all runs.
  old_faults    = []    # the list of previously tried faults
  old_solutions = []    # the list of previously tried solutions
  triggerFault  = None  # the current fault to inject
  solution      = []    # generated after running LDFI with the chosen trigger fault
  conclusion    = None  # bug conclusion = None / FoundCounterexample / NoCounterexampleFound

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

    #if self.core.fault_id == 3 :
    #  tools.bp( __name__, inspect.stack()[0][3], "fucking shit" )

    if DEBUG :
      print "============================================="
      print "            FAULT MANAGER RUN()"
      print "============================================="
      print "    fault_id      = " + str( self.core.fault_id )
      print "    triggerFault  = " + str( self.triggerFault )
      print "    old_faults    = " + str( self.old_faults )
      print "    old_solutions = " + str( self.old_solutions )
      print "---------------------------------------------"

    while True :

      # run LDFI workflow and gather results
      # results := [ conclusion/None, provTree_fmla/None, solution/None ]
      results = self.core.run_workflow( self.triggerFault, self.provTree_fmla )

      # grab data from run
      # provTree_fmla       is not None iff no conclusion exists.
      # likewise, solution  is not None iff no conclusion exists.
      self.conclusion    = results[0]
      self.provTree_fmla = results[1]
      self.solution      = results[2]

      if DEBUG :
        print "**************************************************************"
        print "* FAULT MANAGER RUN() : fault_id = " + str( self.core.fault_id )
        print "* self.conclusion    = "             + str( self.conclusion      )
        print "* self.provTree_fmla = "             + str( self.provTree_fmla   )
        print "* self.solution      = "             + str( self.solution        )
        print "* COMPLETED run_workflow() for "     + str( self.triggerFault    )
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

    # CASE 2 : if conclusion is NoCounterexampleFound and new soln identical to previous soln.
    # TODO : this is PYCOSAT specific. generalize.
    # assumes pycosat just returns last soln in list even if currSolnAttempt surpasses number of solns in list.
    elif self.conclusion == "NoCounterexampleFound" and len( self.old_solutions ) > 0 and self.solution == self.old_solutions[-1] :
      print "display result info..."
      return False


    ####################
    #  RECURSIVE CASE  #
    ####################
    # otherwise, have not hit a conclusion yet
    # RECURSIVE CASE : if NoCounterexampleFound and new solutions exist, then find a new soln and try again.
    else :

      if DEBUG :
        print str( self.triggerFault ) + " : self.conclusion = " + str( self.conclusion )
        print str( self.triggerFault ) + " : self.solution   = " + str( self.solution )

      # add solution to evaluate to old_solutions
      self.old_solutions.append( self.solution )

      # clean solution into a trigger fault
      self.triggerFault = self.getTrigger( self.solution )

      if DEBUG :
        print "solution from previous run_workflow = " + str( self.solution )
        print "triggerFault for next run_workflow  = " + str( self.triggerFault )

      # add new faults to old_faults
      # if seen triggerFault before, iterate again with previous triggerFault
      if not self.triggerFault and self.triggerFault in self.old_faults :
        self.old_faults.append( self.triggerFault )

      # increment the fault id
      self.core.fault_id += 1

      # loop until counterexample found or run out of new solutions
      return True


  #################
  #  GET TRIGGER  #
  #################
  # positive clock facts imply the execution was good because the facts DID NOT happen.
  # handling these is future work.
  def getTrigger( self, soln ) :

    if DEBUG :
      print "IN GETTRIGGER()"

    # self comms are (currently) pointless
    #soln = self.core.removeSelfComms( self.solution )

    triggerFault = []
    for literal in soln :

      if DEBUG :
        print "* literal = " + str( literal )

      if "clock(" in literal :                # trigger faults contain only clock facts
        if "NOT" in literal :                 # do not include positive clock facts
          triggerFault.append( literal[4:] )  # strip off the NOT

    return triggerFault


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return str( self.core.fault_id ) + " : " + str( self.triggerFault )



#########
#  EOF  #
#########
