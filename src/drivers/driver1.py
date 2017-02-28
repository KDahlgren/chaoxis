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
from solvers    import EncodedProvTree_CNF, newProgGenerationTools, solverTools

# **************************************** #


#############
#  GLOBALS  #
#############
DRIVER_DEBUG            = True
RUN_C4_DIRECTLY         = True
PROV_TREES_ON           = True  # toggle prov tree generation code
OUTPUT_PROV_TREES_ON    = False # output prov tree renders
ONE_CORE_ITERATION_ONLY = False
TREE_CNF_ON             = True  # toggle provTree to CNF conversion
OUTPUT_TREE_CNF_ON      = False # toggle CNF formula renders
SOLVE_TREE_CNF_ON       = True  # toggle CNF solve



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

  runTranslator   = True
  tableListPath   = None 
  datalogProgPath = None 
  irCursor        = None
  saveDB          = None
  triedSolnList   = []
  breakBool       = False
  while True :

    if breakBool :
      break

    executionData   = LDFICore( argDict, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList )
    parsedResults   = executionData[0] 
    runTranslator   = executionData[1] # a value indicating whether the db is appropriately populated
    tableListPath   = executionData[2]
    datalogProgPath = executionData[3]
    irCursor        = executionData[4]
    saveDB          = executionData[5]
    triedSolnList   = executionData[6]
    breakBool       = executionData[7]

    if ONE_CORE_ITERATION_ONLY : # only run a single iteration of LDFI
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
      if evalTools.bugFreeExecution( parsedResults, argDict ) :
        pass
      else : # bug exists!!!
        # place magic post processing and visualization code here. =]
        print "HIT BUGGER!!!"
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
def LDFICore( argDict, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList ) :

  print
  print "*******************************************************"
  print "                 RUNNING LDFI CORE"
  print "*******************************************************"
  print

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

      # initialize provenance tree structure
      provTreeComplete = ProvTree.ProvTree( "UltimateGoal", parsedResults, irCursor )

      # grab the set of post records at EOT.
      # assume the right-most attribute/variable/field of the post schema
      # represents the last send time (aka EOT).
      eot = argDict[ "EOT" ]
      postrecords_all = parsedResults[ "post" ]
      postrecords_eot = []
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

      for seedRecord in postrecords_eot :
        if DRIVER_DEBUG :
          print " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
          print "           NEW POST RECORD "
          print "seedRecord = " + str( seedRecord )
        newProvTree = provTreeComplete.generateProvTree( seedRecord )
        provTreeComplete.subtrees.append( newProvTree )

      if OUTPUT_PROV_TREES_ON :
        print "provTreeComplete :"
        provTreeComplete.createGraph( )

    else :
      sys.exit( "ERROR: No path to c4 results file.\nAborting..." ) # sanity check

  # -------------------------------------------- #
  # graphs to CNF
  if TREE_CNF_ON :

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

    if DRIVER_DEBUG and solns :
      numid    = 1

      # +++++++++++++++++++++++++++++++++++++++++++++ #
      print "***************************"
      print "*    PRINTING ALL SOLNS    "
      print "***************************"
      for s in solns.solutions() :
        numsolns = solns.numsolns

        # make pretty
        final = []
        for var in s :
          final.append( solverTools.toggle_format_str( var, "legible" ) )

        if DRIVER_DEBUG :
          print "SOLN : " + str(numid) + " of " + str( numsolns ) + "\n" + str( final )
          numid += 1

      # +++++++++++++++++++++++++++++++++++++++++++++ #
      print "*******************************"
      print "*    PRINTING MINIMAL SOLNS   *"
      print "*******************************"
      numid = 1

      # get solution set
      # formatted as an array of frozen sets
      minimalSolnSet = solns.minimal_solutions()

      finalSolnList = []
      for s in minimalSolnSet :
        numsolns = solns.numsolns

        # make pretty
        for var in s :
          finalSolnList.append( solverTools.toggle_format_list( var, "legible" ) )

        if DRIVER_DEBUG :
          print "SOLN : " + str(numid) + " of " + str( numsolns ) + "\n" + str( final )
          numid += 1

  # -------------------------------------------- #
  # new datalog prog
  breakBool = False
  finalSolnList  = listDiff( finalSolnList, triedSolnList )
  if not finalSolnList == [] :
    executionInfo   = newProgGenerationTools.buildNewProg( finalSolnList, irCursor )
    newProgSavePath = executionInfo[0]
    triedSoln       = executionInfo[1]

    if triedSoln == None :
      if DRIVER_DEBUG :
        print "NO BUGGERS!!!!! Bwa ha ha! *proceeds to laugh manically*"
        breakBool = True
    else :
      triedSolnList.append( triedSoln )  # add to list of tried solns

  else :
    tools.bp( __name__, inspect.stack()[0][3], "HIT BUGGER!!!!! Bwa ha ha! *proceeds to laugh manically*" )

  print "finalSolnList = " + str( finalSolnList )
  print "triedSolnList = " + str( triedSolnList )
  #tools.bp( __name__, inspect.stack()[0][3], "bp" )

  # -------------------------------------------- #
  return ( parsedResults, runTranslator, tableListPath, datalogProgPath, irCursor, saveDB, triedSolnList, breakBool )


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
