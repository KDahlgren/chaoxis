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
  conclusion   = None
  triggerFault = None
  cnf_fmla     = None
  solutions    = []
  descendants  = []

  old_faults   = None

  fault_id     = None # a string of integers.

  # files saving data dump and intermediate file locations
  c4_dump_savepath  = None
  table_list_path   = None
  datalog_prog_path = None

  argDict           = None # dictionary of command line arguments
  cursor            = None # reference to the IR database

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, trigfault, fault_id, old_faults, c4_save, table_save, datalog_save, argDict, cursor ) :

    # initalize lists to empty
    self.solutions         = []
    self.descendants       = []

    # set values
    self.triggerFault      = trigfault
    self.fault_id          = fault_id
    self.old_faults        = old_faults

    self.c4_dump_savepath  = c4_save
    self.table_list_path   = table_save
    self.datalog_prog_path = datalog_save
    self.argDict           = argDict
    self.cursor            = cursor


  #########
  #  RUN  #
  #########
  # run the LDFI core on this trigger fault
  # LDFICore returns [ conclusion/None, cnf_formula/None, solutions/None ]
  # solutions := solutions to the cnf_formula
  # returns a conclusion string
  def run( self ) :

    if DEBUG :
      print "============================================="
      print "            FAULT MANAGER RUN()"
      print "============================================="
      print "    fault_id     = " + str( self.fault_id )
      print "    triggerFault = " + str( self.triggerFault )
      print "    old_faults   = " + str( self.old_faults )

    core            = LDFICore.LDFICore( self.c4_dump_savepath, self.table_list_path, self.datalog_prog_path, self.argDict, self.cursor )
    results         = core.run_workflow( self.triggerFault, self.fault_id )  # [ conclusion/None, cnf_formula/None, solutions/None ]
    self.conclusion = results[0]

    if DEBUG :
      print str( self.triggerFault ) + " : results = " + str( results ) 

    # add evaluated triggerFault to old_solns
    self.old_faults.append( self.triggerFault )

    # if conclusion is not None, then a conclusion exists. return conclusion.
    if self.conclusion :
      return self.conclusion

    # otherwise, have not hit a conclusion in this branch yet.
    else :
      self.cnf_formula = results[1] # pull the cnf formula

      # CNF formula is not None iff no conclusion exists.
      if self.cnf_formula :

        self.solutions = results[2] # pull the solutions to that CNF formula
        self.setDescendants()       # set the descendants for this FaultManager node.

        if DEBUG :
          print str( self.triggerFault ) + " : self.conclusion  = " + str( self.conclusion )
          print str( self.triggerFault ) + " : self.cnf_formula = " + str( self.cnf_formula.display() )
          print str( self.triggerFault ) + " : self.solutions   = " + str( self.solutions )
          print str( self.triggerFault ) + " : len(self.descendants) = " + str(len(self.descendants))

        conclTypes = ConclusionTypes.ConclusionTypes() # instantiate a conclusion types instance

        # iterate over descendant fault hypotheses.
        # the looping protocol amounts to a depth-first search over the hypos.
        for i in range( 0,len( self.descendants ) ) :

          if DEBUG :
            print "iterate over descendant : " + self.descendants[i].display()

          desc = self.descendants[i]

          if desc.triggerFault in self.old_faults :
            pass
          else :
            concl = desc.run()

            if concl :
              print "<><>triggerFault = " + str(desc.triggerFault) + " : concl = " + concl

              # CASE : 'NoCounterexampleFound'
              if conclTypes.categories[0] in concl :
                if not i == len( self.descendants ) - 1 :
                  pass
                else :
                  return concl

              # CASE : 'FoundCounterexample'
              elif conclTypes.categories[1] in concl :
                return concl

              else :
                tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized conclusion type " + str(concl) )
            else :
              tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : run on trigger fault " + str(desc.triggerFault) + " resulted in a None conclusion. Aborting..." )
      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : self.cnf_formula is None" )

    if DEBUG :
      print "COMPLETED run() for " + str(self.triggerFault)


  #####################
  #  SET DECSENDANTS  #
  #####################
  # the descendants of a fault manager rooted at a non-terminating fault are fault managers.
  def setDescendants( self ) :

    #self.descendants = [] # ???? why is this needed? Shit's up by adding extra elements otherwise. >.>

    allFaultHypos = self.getAllFaultHypos( self.solutions ) # the power set of all fault combos in solnList

    # iterate over the solutions to the cnf formula
    for i in range( 0, len( allFaultHypos ) ) :

      faultHypos_oneSoln = allFaultHypos[i]

      # iterate over the powerset of the current solution
      for j in range( 0, len( faultHypos_oneSoln ) ) :

        fh          = faultHypos_oneSoln[j]
        fh_fault_id = self.fault_id + str(i) + str(j) # create new fault id for this descendant
        print "self.fault_id = " + self.fault_id + "; fh_fault_id = " + fh_fault_id

        # create the new fault manager
        fh_fm = FaultManager( fh, fh_fault_id, self.old_faults, self.c4_dump_savepath, self.table_list_path, self.datalog_prog_path, self.argDict, self.cursor )

        print "fh_fm.display() = " + fh_fm.display()

        self.descendants.append( fh_fm )

    for d in self.descendants :
      print ">>> d.display() = " + d.display()

  #########################
  #  GET ALL FAULT HYPOS  #
  #########################
  # return the powerset of every soln in solnList, sans the empty sets.
  def getAllFaultHypos( self, solnList ) :

    allsets = []

    for soln in solnList :
      #allsets.append( self.powerset( soln ) )
      allsets.append( self.unaryOnly( soln ) )

    return allsets


  ###############
  #  POWER SET  #
  ###############
  # from https://rosettacode.org/wiki/Power_set#Python
  def powerset( self, soln ) :

    result = [[]]
    for fact in soln :
      # for every additional element in our set
      # the power set consists of the subsets that don't
      # contain this element (just take the previous power set)
      # plus the subsets that do contain the element (use list
      # comprehension to add [x] onto everything in the
      # previous power set)
      result.extend( [ subset + [ fact ] for subset in result ] )
    
    return result[1:] # remove the empty set


  ###########
  #  UNARY  #
  ###########
  def unaryOnly( self, soln ) :

    result = []
    for s in soln :
      result.append( [s] )

    return result


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return self.fault_id + " : " + str( self.triggerFault )



#########
#  EOF  #
#########
