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
import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from dedt import dedt, dedalusParser
from utils import parseCommandLineInput
# ------------------------------------------------------ #

DRIVER_DEBUG = True

# **************************************** #

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
  if( len(argList) < 1 ) :
    thisFilename = os.path.basename(__file__)     # name of this file
    print "No arguments provided. Please run 'python " + sys.argv[0] + " -h' for assistance."
    sys.exit()

  # pass list to parse args, get dict of args
  argDict = parseArgs( )
  print argDict

  # translate all input dedalus files into a single datalog program
  datalogProgPath = dedt.translateDedalus( argDict )
  if DRIVER_DEBUG :
    print "datalog program path = " + datalogProgPath

  # run through pydatalog, collect bindings ~ provenance
  # if buggy => output results
  # else => ...

  print "PASSED" # needed for simpleLog in tests/
                 # TODO: create more robust testing framework

#########################
#  THREAD OF EXECUTION  #
#########################
driver()

#########
#  EOF  #
#########
