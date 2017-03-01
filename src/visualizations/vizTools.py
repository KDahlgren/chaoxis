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

from dedt       import dedt, dedalusParser
from derivation import ProvTree
from utils      import parseCommandLineInput, tools
from evaluators import c4_evaluator, evalTools
from solvers    import EncodedProvTree_CNF, newProgGenerationTools, solverTools

# **************************************** #


################################
#  GENERATE BUGGY PROV GRAPHS  #
################################
def generateBuggyProvGraphs() :
  return None


#########
#  EOF  #
#########
