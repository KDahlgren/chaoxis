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
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from derivation import ProvTree
from utils      import tools

# **************************************** #


DEBUG = True

################################
#  GENERATE BUGGY PROV GRAPHS  #
################################
def generateBuggyProvGraphs( parsedResults, eot, irCursor ) :

  if DEBUG :
    print
    print "000000000000000000000000000000000000"
    print "0   GENERATING BUGGY PROV GRAPHS   0"
    print "000000000000000000000000000000000000"
    print

  # discover the set of goal nodes possessing records for eot.
  # do not need to worry about overlapping graphs because pydot ignores duplicates.
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

  # generate a provenance graph for each goal node.

  # output the progenance graphs in a single render.

  return None


#########
#  EOF  #
#########
