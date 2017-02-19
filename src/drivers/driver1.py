#!/usr/bin/env python

'''
driver1.py
  A driver exemplifying the orchestration of the
  implemented LDFI workflow.
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from dedt       import dedt, dedalusParser
from derivation import ProvTree
from utils      import parseCommandLineInput, tools
from evaluators import c4_evaluator, evalTools
from solvers    import CNF_tools

# **************************************** #

DRIVER_DEBUG     = True
RUN_C4_DIRECTLY  = True
PROV_TREES_ON    = True
ONEITERATIONONLY = True

################
#  PARSE ARGS  #
################
# parse arguments from the command line
def parseArgs( ) :
  argDict = {}   # empty dict

  argDict = parseCommandLineInput.parseCommandLineInput( )  # get dictionary of arguments.

  return argDict

####################
#  PASS TO SOLVER  #
####################
# pass dedalus programs and arguments to solver
def passToSolver() :
  print " ... In passToSolver ..."
  #

####################
#  OUTPUT RESULTS  #
####################
# output results =]
def outputResults() :
  print " ... In outputResults ..."
  #

############
#  DRIVER  #
############
def driver() :
  # get list of command line args, except prog name
  argList = sys.argv[1:]

  # print help if no args provided
  if len(argList) < 1 :
    thisFilename = os.path.basename(__file__)     # name of this file
    sys.exit( "No arguments provided. Please run 'python " + sys.argv[0] + " -h' for assistance." )

  # ----------------------------------------------- #

  # pass list to parse args, get dict of args
  argDict = parseArgs( )
  print argDict

  # =================================================================== #
  # loop until find a bug.

  while True :

    executionData = LDFICore( argDict )
    parsedResults = executionData[0] 
    irCursor      = executionData[1]
    saveDB        = executionData[2]

    if ONEITERATIONONLY : # only run a single iteration of LDFI
      break

    else :
      # sanity check
      if not "pre" in parsedResults :
        dedt.cleanUp( irCursor, saveDB )
        tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining pre" )
      elif not "post" in parsedResults :
        dedt.cleanUp( irCursor, saveDB )
        tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining post" )

      # check for bug
      if evalTools.bugFreeExecution( parsedResults ) :
        pass
      else : # bug exists!!!
        # place magic post processing and visualization code here. =]
        break

  # =================================================================== #

  # -------------------------------------------- #
  # cleanUp saved db stuff
  dedt.cleanUp( irCursor, saveDB )

  # -------------------------------------------- #
  # sanity check
  print "PROGRAM EXITED SUCCESSFULLY"


###############
#  LDFI CORE  #
###############
def LDFICore( argDict ) :
  # ----------------------------------------------- #

  # translate all input dedalus files into a single datalog program
  outputs         = dedt.translateDedalus( argDict )
  tableListPath   = outputs[0] # string of table names
  datalogProgPath = outputs[1] # path to datalog program
  irCursor        = outputs[2] # ir db cursor
  saveDB          = outputs[3] # ir db save file

  if DRIVER_DEBUG :
    print "outputs              = " + str( outputs )
    print "table   list    path = " + tableListPath
    print "datalog program path = " + datalogProgPath

  # ----------------------------------------------- #
  # evaluate

  resultsPath = None

  # c4
  savepath = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"
  if RUN_C4_DIRECTLY :
    resultsPath = c4_evaluator.runC4_directly( datalogProgPath, tableListPath, savepath )
  else :
    c4_evaluator.runC4_wrapper( datalogProgPath, tableListPath )

  # ----------------------------------------------- #
  # get provenance trees
  if PROV_TREES_ON :
    if resultsPath :
      print "Using c4 results from : " + resultsPath
      parsedResults = tools.getEvalResults_file_c4( resultsPath )

      provTreeComplete = ProvTree.ProvTree( "UltimateGoal", parsedResults, irCursor )
      for seedRecord in parsedResults[ "post" ] :
        if DRIVER_DEBUG :
          print " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
          print "           NEW POST RECORD "
          print "seedRecord = " + str( seedRecord )
        newProvTree = provTreeComplete.generateProvTree( seedRecord )
        provTreeComplete.subtrees.append( newProvTree )

      if DRIVER_DEBUG :
        print "provTreeComplete :"
        provTreeComplete.createGraph( )

    else :
      sys.exit( "ERROR: No path to c4 results file.\nAborting..." ) # sanity check


  # -------------------------------------------- #
  # graphs to CNF
  fmla = CNF_tools.convertToCNF( provTreeComplete )

  # -------------------------------------------- #
  # solve CNF
  # magic code here...
  # solns = //.solveCNF( fmla )

  # -------------------------------------------- #
  # new datalog prog
  # magic code here...
  # newProg = //.generateNewClock( solns )

  return ( parsedResults, irCursor, saveDB )

#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
