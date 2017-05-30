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
DEBUG = False

C4_DUMP_SAVEPATH  = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"
TABLE_LIST_PATH   = os.path.abspath( __file__ + "/../.."    ) + "/evaluators/programFiles/" + "tableListStr.data"
DATALOG_PROG_PATH = os.path.abspath( __file__ + "/../.."    ) + "/evaluators/programFiles/" + "c4program.olg"


############
#  DRIVER  #
############
def driver() :

  os.system( "rm IR.db" ) # delete db from previous run, if appicable

  # get dictionary of commandline arguments.
  # exits here if user provides invalid inputs.
  argDict = driverTools.parseArgs( )

  # instantiate IR database
  saveDB = os.getcwd() + "/IR.db"
  IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor = IRDB.cursor()

  # initialize fault manager
  fm = FaultManager.FaultManager( C4_DUMP_SAVEPATH, TABLE_LIST_PATH, DATALOG_PROG_PATH, argDict, cursor )
  fm.run()

  os.system( "rm IR.db" ) # delete db from previous run, if appicable

  if DEBUG :
    "PROGRAM ENDED SUCESSFULLY."

#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
