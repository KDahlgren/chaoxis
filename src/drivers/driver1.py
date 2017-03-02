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
RUN_C4_DIRECTLY         = True
PROV_TREES_ON           = True  # toggle prov tree generation code
OUTPUT_PROV_TREES_ON    = True  # output prov tree renders
ONE_CORE_ITERATION_ONLY = False
TREE_CNF_ON             = True  # toggle provTree to CNF conversion
OUTPUT_TREE_CNF_ON      = False # toggle CNF formula renders
SOLVE_TREE_CNF_ON       = True  # toggle CNF solve

C4_DUMP_SAVEPATH        = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"


################
#  PARSE ARGS  #
################
# parse arguments from the command line
def parseArgs( ) :
  argDict = {}   # empty dict

  argDict = parseCommandLineInput.parseCommandLineInput( )  # get dictionary of arguments.

  return argDict


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

  # check if EOT is an integer (this better pass!)
  try :
    val = int( argDict[ "EOT" ] )
  except :
    tools.bp( __name__, inspect.stack()[0][3], " Could not convert EOT into integer: EOT = " + str(eot) )

  # =================================================================== #
  # loop until find a bug (or not).

  ITER_COUNT      = 0
  runTranslator   = True
  tableListPath   = None 
  datalogProgPath = None 
  irCursor        = None
  saveDB          = None
  triedSolnList   = []
  executionStatus = None
  while True :

    executionData   = LDFICore( argDict, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList, ITER_COUNT )

    parsedResults   = executionData[0] 
    runTranslator   = executionData[1] # a value indicating whether the db is appropriately populated
    tableListPath   = executionData[2]
    datalogProgPath = executionData[3]
    irCursor        = executionData[4]
    saveDB          = executionData[5]
    if executionData[6] :
      triedSolnList   = executionData[6]
    executionStatus = executionData[7]

    ITER_COUNT += 1
    # ---------------------------------------------------------------------- #
    # control loop iterations
    if ONE_CORE_ITERATION_ONLY : # only run a single iteration of LDFI (good for debugging)
      break

    else :
      # sanity check pre and post must appear in the evaluation results.
      if not "pre" in parsedResults :
        dedt.cleanUp( irCursor, saveDB )
        tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining pre" )
      elif not "post" in parsedResults :
        dedt.cleanUp( irCursor, saveDB )
        tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining post" )

      # check for bug
      if evalTools.bugFreeExecution( parsedResults, argDict[ 'EOT' ], executionStatus ) :
        pass
      else : # bug exists!!!
        # place magic post processing and visualization code here. =]
        print "HIT BUGGER!!!"

        if DRIVER_DEBUG :
          print 
          print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          print "    RUNNING POST PROCESSING"
          print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          print 

        # generate prov graphs of buggy executions.
        vizTools.generateBuggyProvGraphs( parsedResults, argDict[ "EOT" ], irCursor, ITER_COUNT )

        break
    # ---------------------------------------------------------------------- #

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
def LDFICore( argDict, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList, iter_count ) :


  print
  print "*******************************************************"
  print "                 RUNNING LDFI CORE"
  print "*******************************************************"
  print

  os.system( "rm " + C4_DUMP_SAVEPATH )

  # ----------------------------------------------- #

  # translate all input dedalus files into a single datalog program
  outputs = None
  if runTranslator :
    outputs         = dedt.translateDedalus( argDict )
    tableListPath   = outputs[0] # string of table names
    datalogProgPath = outputs[1] # path to datalog program
    irCursor        = outputs[2] # ir db cursor
    saveDB          = outputs[3] # ir db save file
    runTranslator   = False

  if DRIVER_DEBUG :
    if outputs :
      print "outputs              = " + str( outputs )
    print "table   list    path = " + tableListPath
    print "datalog program path = " + datalogProgPath

  # ----------------------------------------------- #
  # evaluate

  resultsPath = None

  # c4
  savepath = C4_DUMP_SAVEPATH
  if RUN_C4_DIRECTLY :
    resultsPath = c4_evaluator.runC4_directly( datalogProgPath, tableListPath, savepath )
  else :
    c4_evaluator.runC4_wrapper( datalogProgPath, tableListPath )

  # ----------------------------------------------- #
  # get provenance trees
  if PROV_TREES_ON :


    if DRIVER_DEBUG :
      print "\n~~~~ BUILDING PROV TREE ~~~~"

    if resultsPath :
      print "Using c4 results from : " + resultsPath
      parsedResults = tools.getEvalResults_file_c4( resultsPath )

      # initialize provenance tree structure
      provTreeComplete = ProvTree.ProvTree( "FinalState", parsedResults, irCursor )

      # grab the set of post records at EOT.
      # assume the right-most attribute/variable/field of the post schema
      # represents the last send time (aka EOT).
      eot = argDict[ "EOT" ]
      postrecords_all = parsedResults[ "post" ]
      postrecords_eot = []

      if DRIVER_DEBUG :
        print "postrecords_all = " + str(postrecords_all)

      for rec in postrecords_all :
        print "rec     = " + str(rec)
        print "rec[-1] = " + str(rec[-1])
        print "eot     = " + str(eot)

        # check if last element of post record is an integer
        try :
          val = int( rec[-1] )
        except :
          tools.bp( __name__, inspect.stack()[0][3], " Could not convert last element of record " + str(rec) + ", rec[-1] = " + str(rec[-1]) + " into an integer. Therefore, cannot compare with EOT." )

        # collect eot post records only
        if int( rec[-1] ) == int( eot ) :
          postrecords_eot.append( rec )

      #
      # !!! RETURN EARLY IF POST CONTAINS NO EOT RECORDS !!!
      if len( postrecords_eot ) < 1 :
        return ( parsedResults, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, None, "nomoreeotpostrecords")

      if iter_count == 1 :
        tools.bp( __name__, inspect.stack()[0][3], "iter_count = " + str(iter_count) )

      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
      # populate prov tree
      for seedRecord in postrecords_eot :
        if DRIVER_DEBUG :
          print " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
          print "           NEW POST RECORD "
          print "seedRecord = " + str( seedRecord )
        newProvTree = provTreeComplete.generateProvTree( "post", seedRecord )
        provTreeComplete.subtrees.append( newProvTree )
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

      if OUTPUT_PROV_TREES_ON :
        print "provTreeComplete :"
        provTreeComplete.createGraph( None, iter_count )

    else :
      sys.exit( "ERROR: No path to c4 results file.\nAborting..." ) # sanity check

  # -------------------------------------------- #
  # graphs to CNF


  if TREE_CNF_ON and PROV_TREES_ON :

    if DRIVER_DEBUG :
      print "\n~~~~ CONVERTING PROV TREE TO CNF ~~~~"

    provTree_fmla = EncodedProvTree_CNF.EncodedProvTree_CNF( provTreeComplete ) # get fmla with provTree_fmla.CNFFormula

    if provTree_fmla.rawformula :
      print ">>> provTree_fmla.rawformula = " + str( provTree_fmla.rawformula )
      print
      print ">>> provTree_fmla.rawformula.display() = " + str( provTree_fmla.rawformula.display() )
      print
      print ">>> provTree_fmla.cnfformula = " + str( provTree_fmla.cnfformula )
      print

      if OUTPUT_TREE_CNF_ON :
        provTree_fmla.rawformula.graph()

    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: provTree_fmla.rawformula is empty. Aborting execution..." )

  # -------------------------------------------- #
  # solve CNF
  if SOLVE_TREE_CNF_ON :
    solns = solverTools.solveCNF( provTree_fmla.cnfformula )

    # sanity check
    if DRIVER_DEBUG :
      print "***************************"
      print "*    PRINTING ALL SOLNS    "
      print "***************************"

    # +++++++++++++++++++++++++++++++++++++++++++++ #
    # collect solns and process into legible format
    if solns :
      numid    = 1

      finalSolnList = []
      finalStr = []
      for s in solns.solutions() :
        numsolns = solns.numsolns

        # make pretty
        for var in s :
          finalStr.append( solverTools.toggle_format_str( var, "legible" ) )

        if DRIVER_DEBUG :
          print "SOLN : " + str(numid) + " of " + str( numsolns ) + "\n" + str( finalStr )
          numid += 1

        # add soln to soln list and clear temporary save list for the next iteration
        finalSolnList.append( finalStr )
        finalStr = []

      # duplicates are annoying.
      tmp = []
      for s in finalSolnList :
        if s : # skip empties
          if not s in tmp :
            tmp.append( s )
      finalSolnList = tmp

    else :
      tools.bp( __name__, inspect.stack()[0][3], "Congratulations! No solutions exist, meaning the solver could not find a counterexample. Aborting..." )
    # +++++++++++++++++++++++++++++++++++++++++++++ #

  # -------------------------------------------- #
  # new datalog prog
  if DRIVER_DEBUG :
    print "before: finalSolnList = " + str( finalSolnList )

  finalSolnList  = listDiff( finalSolnList, triedSolnList ) # remove triedSolns from list

  if DRIVER_DEBUG :
    print "after: finalSolnList = " + str( finalSolnList )
    print "triedSolnList = " + str( triedSolnList )

  # case the finalSolnList still contains clock-only solns
  if not clockFree( finalSolnList ) :
    executionInfo   = newProgGenerationTools.buildNewProg( finalSolnList, irCursor )
    newProgSavePath = executionInfo[0]
    triedSoln       = executionInfo[1]
    triedSolnList.append( triedSoln )  # add to list of tried solns

  # -------------------------------------------- #
  return ( parsedResults, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList, "GOOD" )


################
#  CLOCK FREE  #
################
# check if any solns contain only clock facts
# return False if solns containing only clock facts exist
def clockFree( finalSolnList ) :

  vals = []
  for soln in finalSolnList :     # check if each soln contains only clock facts
    valid = True # be optimistic
    for var in soln :
      if not "clock(" in var :
        valid = False
    vals.append( valid )

  # case there exists at least one clock-only soln,
  #  then the solution list is not clock free
  if True in vals :
    return False
  else :
    return True


###############
#  LIST DIFF  #
###############
def listDiff( finalList, triedList ) :

  newFinal = []

  for item in finalList :
    if not item in triedList :
      newFinal.append( item )

  return newFinal


#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
