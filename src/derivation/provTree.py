#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath )

import DerivTree, GoalNode, RuleNode, FactNode

# **************************************** #

DEBUG = False

# --------------------------------------------------- #

#########################
#  GENERATE PROVE TREE  #
#########################
def generateProvTree( seedRecord, fullResults, cursor ) :
  return DerivTree.DerivTree( "post", "goal", False, seedRecord, fullResults, cursor )

# --------------------------------------------------- #

######################
#  GET EVAL RESULTS  #
######################
# get results from c4 output file
def getEvalResults_file( path ) :

  if os.path.exists( path ) :
    fo = open( path )

    prevLine = None
    currRel  = None

    resultsDict = {}
    save        = False
    tupleList   = []

    for line in fo :

      if line == "\n" :
        resultsDict[ currRel ] = tupleList
        currRel = None
        tupleList = []
        save = False

      elif prevLine == "---------------------------" :
        currRel = line.rstrip()
        save    = True

      elif save == True :
        tupleList.append( line.rstrip() )


      prevLine = line.rstrip()

    fo.close()

  else :
    sys.exit( "Cannot open file : " + path )

  if DEBUG :
    print "resultsDict : "
    for key in resultsDict :
      print "key = " + key + " : "
      print resultsDict[ key ]

  cleanResultsDict = {}
  for key in resultsDict :
    tupList = []
    for tup in resultsDict[ key ] :
      tup = tup.split( "," )
      tupList.append( tup )
    cleanResultsDict[ key ] = tupList

  if DEBUG :
    print "cleanResultsDict : "
    for key in cleanResultsDict :
      print "key = " + key + " : "
      print cleanResultsDict[ key ]

  return cleanResultsDict
