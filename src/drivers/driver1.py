#!/usr/bin/env python

'''
driver1.py
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

import driverTools

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from faultManager import FaultManager

# **************************************** #


#############
#  GLOBALS  #
#############
DEBUG = True

C4_DUMP_SAVEPATH  = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"
TABLE_LIST_PATH   = os.path.abspath( __file__ + "/../.."    ) + "/evaluators/programFiles/" + "tableListStr.data"
DATALOG_PROG_PATH = os.path.abspath( __file__ + "/../.."    ) + "/evaluators/programFiles/" + "c4program.olg"


############
#  DRIVER  #
############
def driver() :

  # get dictionary of commandline arguments.
  # exits here if user provides invalid inputs.
  argDict = driverTools.parseArgs( )

  # instantiate IR database
  saveDB = os.getcwd() + "/IR.db"
  IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor = IRDB.cursor()

  # paths to datalog files
  tablePath   = None
 
  # track number of LDFI core executions
  iter_count = 0

  # fault hypothesis data from previous iterations
  prev_cnf_fmla            = None

  # important collection vars
  all_suggested_faultHypos = []
  final_faultHypo          = None
  final_explanation        = None


  # initialize fault manager
  initial_trigger_fault = []
  initial_fault_id      = "0"
  fm = FaultManager.FaultManager( initial_trigger_fault, initial_fault_id, [], C4_DUMP_SAVEPATH, TABLE_LIST_PATH, DATALOG_PROG_PATH, argDict, cursor )
  fm.run()

  if DEBUG :
    "PROGRAM ENDED SUCESSFULLY."

#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
