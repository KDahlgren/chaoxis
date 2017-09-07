#!/usr/bin/env python

'''
vizTools.py
  Details processes for visulaizing execution results.
  Post processing.
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

# ------------------------------------------------------ #
# import orik packages HERE!!!
if not os.path.abspath( __file__ + "/../../../lib/orik/src") in sys.path :
  sys.path.insert(0, os.path.abspath( __file__ + "/../../../lib/orik/src") )

from derivation import ProvTree

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils      import tools

# **************************************** #


DEBUG = tools.getConfig( "VISUALIZATIONS", "VIZTOOLS_DEBUG", bool )


################################
#  GENERATE BUGGY PROV GRAPHS  #
################################
def generateBuggyProvGraphs( parsedResults, eot, irCursor, iter_count ) :

  if DEBUG :
    print
    print "000000000000000000000000000000000000"
    print "0   GENERATING BUGGY PROV GRAPHS   0"
    print "000000000000000000000000000000000000"
    print

  # ------------------------------------------------------------- #
  # discover the set of goal nodes possessing records for eot.
  # do not need to worry about overlapping or redundant 
  # graphs because pydot ignores duplicates.
  validGoals = []
  for key in parsedResults :
    if not "_prov" in key : # skip provenance goals
      valid = False # glass half empty
      for rec in parsedResults[ key ] :
        if str(eot) in rec[-1] :
          valid = True
      if valid :
        validGoals.append( key )

  if DEBUG :
    print "validGoals = " + str( validGoals )

  # ------------------------------------------------------------- #
  # generate a provenance graph for each goal node.

  # initialize provenance tree structure
  provTree_buggy = ProvTree.ProvTree( "FinalState", parsedResults, irCursor )

  # populate prov tree
  for goal in validGoals :
    for seedRecord in parsedResults[ goal ] :
      if str(eot) in seedRecord[-1] :
        newProvTree = provTree_buggy.generateProvTree( goal, seedRecord )
        provTree_buggy.subtrees.append( newProvTree )

  # ------------------------------------------------------------- #
  # output the progenance graphs in a single render.
  provTree_buggy.createGraph( "buggyGraph", iter_count )


#########
#  EOF  #
#########
