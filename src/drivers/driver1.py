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
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

import driverTools

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from dedt           import dedt, dedalusParser
from derivation     import ProvTree
from utils          import parseCommandLineInput, tools
from evaluators     import c4_evaluator, evalTools
from solvers        import EncodedProvTree_CNF, newProgGenerationTools, solverTools
from visualizations import vizTools

# **************************************** #


#############
#  GLOBALS  #
#############
DRIVER_DEBUG            = True
ONE_CORE_ITERATION_ONLY = False
CMDLINE_RESULTS_OUTPUT  = True

C4_DUMP_SAVEPATH        = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"
TABLE_LIST_PATH         = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/" + "tableListStr.data"
DATALOG_PROG_PATH       = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/" + "c4program.olg"

PROV_TREES_ON           = True  # toggle prov tree generation code
TREE_CNF_ON             = True  # toggle provTree to CNF conversion


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
  all_suggested_faultHypos = []
  curr_suggested_faultHypo = None
  final_faultHypo          = None
  final_explanation        = None

  # =================================================================== #
  #                        LOOP OVER LDFI CORE                          #
  # =================================================================== #
  while True :

    if DRIVER_DEBUG :
      print "it# " + str(iter_count) + " : curr_suggested_faultHypo = " + str(curr_suggested_faultHypo) 

    executionResults = LDFICore( argDict, iter_count, cursor )

    if ONE_CORE_ITERATION_ONLY : # only run a single iteration of LDFI (good for debugging)
      break

    else :
      isBugFree                = executionResults[0]
      explanation              = executionResults[1]
      execStatus               = executionResults[2]
      curr_suggested_faultHypo = executionResults[3]


      # BUG FREE and no new suggested fault hypothesis
      if isBugFree and (curr_suggested_faultHypo == [] or not curr_suggested_faultHypo) :
          final_faultHypo   = "n/a"
          final_explanation = "no counterexamples found."
          break

      else :

        # hit a bug => break LDFI core and output results
        if not isBugFree :
          final_faultHypo   = curr_suggested_faultHypo
          final_explanation = explanation
          break

        # bug free but no suggested fault hypothesis
        else :
          if DRIVER_DEBUG :
            print "isBugFree                = " + str(isBugFree)
            print "explanation              = " + str(explanation)
            print "execStatus               = " + str(execStatus)
            print "curr_suggested_faultHypo = " + str(curr_suggested_faultHypo)

          #tools.bp( __name__, inspect.stack()[0][3], "wot??? >.>" )
          continue

    if iter_count > 10  :
      tools.bp( __name__, inspect.stack()[0][3], "saving your ass from an infinite loop" )

    iter_count += 1 # directly corresponds with number of LDFI Core iterations

  # =================================================================== #
  #                     END OF INFINTE WHILE LOOP                       #
  # =================================================================== #

  if DRIVER_DEBUG :
    cursor.execute( "SELECT * FROM Crash" )
    res = cursor.fetchall()
    res = tools.toAscii_multiList( res )
    print "/////////////////////////"
    print "CONTENTS OF crash table :"
    for tup in res :
      print tup
    print "/////////////////////////"
    print "NUMBER OF CORE ITERATIONS : " + str(iter_count+1)

  # -------------------------------------------- #

  if CMDLINE_RESULTS_OUTPUT :
    print "/////////////////////////"
    print "~~~ Fault Hypothesis ~~~"
    print str(final_faultHypo)
    print "/////////////////////////"
    print "~~~~~ Explanation ~~~~~"
    print final_explanation
    print "/////////////////////////"

  # -------------------------------------------- #
  # cleanUp saved db stuff
  dedt.cleanUp( cursor, saveDB )

  # always save and remove the last dump file for future reference
  if os.path.isfile( C4_DUMP_SAVEPATH ) :
    os.system( "mv " + C4_DUMP_SAVEPATH + " " + C4_DUMP_SAVEPATH + "_" + time.strftime("%d%b%Y-%Hh%Mm%Ss") + "_final" )

  # -------------------------------------------- #
  # sanity check
  print "PROGRAM EXITED SUCCESSFULLY"


###############
#  LDFI CORE  #
###############
# core LDFI workflow:
#  1. convert dedalus program to some version of datalog
#  2. evaluate the datalog program using some evaluator
#  3. check for bugs
#  4. build the provenance tree for the evaluation execution
#  5. build a CNF formula from the provenance tree
#  6. solve the CNF formula using some solver
#  7. generate the new datalog program for the next iteration
def LDFICore( argDict, iter_count, cursor ) :

  if DRIVER_DEBUG :
    print
    print "*******************************************************"
    print "                 RUNNING LDFI CORE"
    print "*******************************************************"
    print

  # always save the last dump file for future reference
  if os.path.isfile( C4_DUMP_SAVEPATH ) :
    os.system( "mv " + C4_DUMP_SAVEPATH + " " + C4_DUMP_SAVEPATH + "_" + time.strftime("%d%b%Y-%H%M%S") + ".txt" )

  # ----------------------------------------------- #
  # get datalog

  # translate all input dedalus files into a single datalog program
  outputs = None
  if iter_count == 0 :
    driverTools.dedalus_to_datalog( argDict, TABLE_LIST_PATH, DATALOG_PROG_PATH, cursor )

  if DRIVER_DEBUG :
    if outputs :
      print "outputs           = " + str( outputs )
      print "TABLE_LIST_PATH   = " + TABLE_LIST_PATH
      print "DATALOG_PROG_PATH = " + DATALOG_PROG_PATH

  # ----------------------------------------------- #
  # evaluate

  # assuming using C4 at commandline
  resultsPath   = driverTools.evaluate( "C4_CMDLINE", TABLE_LIST_PATH, DATALOG_PROG_PATH, C4_DUMP_SAVEPATH )
  parsedResults = tools.getEvalResults_file_c4( resultsPath ) # assumes C4 results stored in dump

  # ----------------------------------------------- #
  # check for bugs

  bugData             = driverTools.checkForBugs( parsedResults, argDict[ "EOT" ] )
  isBugFree           = bugData[0]
  explanation         = bugData[1]
  execStatus          = bugData[2]
  suggested_faultHypo = None

  # ---------------------------------------------- #
  # check execution status
  check0 = execStatus[0]

  # hit a passing condition
  # e.g. no eot data in pre and no eot data in post.
  # a vacuously good execution.
  if check0 :
    return [ isBugFree, explanation, execStatus, suggested_faultHypo ]

  # ---------------------------------------------- #
  # return early if bug exists
  if not isBugFree :
    return [ isBugFree, explanation, execStatus, suggested_faultHypo ]

  tools.bp( __name__, inspect.stack()[0][3], "parsedResults = \n" + str(parsedResults) )

  # ----------------------------------------------- #
  # get provenance trees
  if PROV_TREES_ON :
    provTreeComplete = driverTools.buildProvTree( parsedResults, argDict[ "EOT" ], iter_count, cursor )

  # -------------------------------------------- #
  # generate CNF formula

  if TREE_CNF_ON and PROV_TREES_ON :
    provTree_fmla = driverTools.tree_to_CNF( provTreeComplete )

  # -------------------------------------------- #
  # solve CNF formula

  finalSolnList = driverTools.solveCNF( provTree_fmla )

  # -------------------------------------------- #
  # generate new datalog prog

  suggested_faultHypo = driverTools.getNewDatalogProg( finalSolnList, cursor, iter_count )

  # -------------------------------------------- #
  # no bug discovered in this execution

  return [ isBugFree, explanation, execStatus, suggested_faultHypo ]


#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
