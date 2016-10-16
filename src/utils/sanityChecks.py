#!/usr/bin/env python

import messages
import os
import sys

#######################
#  CHECK PARENTHESES  #
#######################
def checkParentheses( line ) :
  numOpen   = 0 # number of open parentheses "("
  numClosed = 0 # number of closed parentheses ")"

  for c in line :
    if c == "(" :
      numOpen += 1
    elif c == ")" :
      numClosed += 1

  if not numOpen == numClosed :
    sys.exit( "ERROR: Incorrect number of parentheses in line: " + line )

  return True

###############################
#  CHECK COMMAND LINE INPUTS  #
###############################
#  argList         := the list of all command line inputs (except the name of the script)
def checkCommandLineInputs( argList ) :
  # list of all valid options
  validOptsList = [ '--solver',
                    '--strategy',
                    '--use-symmetry',
                    '--prov-diagrams',
                    '--disable-dot-rendering',
                    '--find-all-counterexamples',
                    '--negative-support',
                    '-t', '--EOT',
                    '-f', '--EFF',
                    '-c', '--crashes',
                    '-n', '--nodes' ]

  # list of all error types
  validKeyList = [ "invalidDedFile",
                   "negValue",
                   "valueTypeError",
                   "invalidInput",
                   "invalidNodeList",
                   "invalidSolver",
                   "invalidStrategy",
                   "missingInput" ]

  # get the list of valid solvers
  validSolverList = [ 'z3', 'ilp' ] # = appConfigs.getValidSolvers()

  # get the list of valid strategies
  validStrategyList = [ 'sat', 'random', 'pcausal' ] # = appConfigs.getValidStrategies()

  # maintain dictionary of invalid argument inputs
  badInputs     = {}
  for k in validKeyList :
    badInputs[ k ] = [] # initialize dict

  # ------------------- #
  # required parameters
  # ------------------- #
  noDedFile      = False
  nodesSpecified = False

  # -------------------------------------------------------------- #

  # check arg list contents
  for i in range(0,len(argList)) :
    currArg = argList[i]     # current argument
    prevArg = ""             # initialize empty
    if i > 0 :
      prevArg = argList[i-1] # previous argument

    # check for ded files
    if ".ded" in currArg :
      noDedFile = False

      # check path
      if not os.path.isfile( currArg ) :
        badInputs[ "invalidDedFile" ].append( [ currArg ] )

    # check if csv for node params
    elif ('-n' == prevArg) or ('--nodes' == prevArg) :
      if (len(currArg) > 1) and (not ',' in currArg) :
        badInputs[ "invalidNodeList" ].append( [ prevArg, currArg ] ) # save bad arguments as a list
      nodesSpecified = True # hit valid nodes param

    # check for missing/bad values
    elif ('-t' == prevArg) or ('--EOT' == prevArg)     or \
         ('-f' == prevArg) or ('--EFF' == prevArg)     or \
         ('-c' == prevArg) or ('--crashes' == prevArg) :

      # check if integer
      try :
        v = int(currArg) # will fail for non-integer values (e.g. strings, floats)
        if v < 0 :
          badInputs[ "negValue" ].append( [ prevArg, currArg ] ) # save bad arguments as a list
      except :
        badInputs[ "valueTypeError" ].append( [ prevArg, currArg ] ) # save bad arguments as a list

    # check for bad strings
    elif (not currArg in validOptsList) and (not currArg in validSolverList) and (not currArg in validStrategyList) :
      badInputs[ "invalidInput" ].append( [ currArg ] ) # save bad arguments as a list

    # check for valid solver
    if '--solver' == prevArg :
      if not currArg in validSolverList :
        badInputs[ "invalidSolver" ].append( [ prevArg, currArg ] ) # save bad arguments as a list

    # check for valid strategy
    if '--strategy' == prevArg :
      if not currArg in validStrategyList :
        badInputs[ "invalidStrategy" ].append( [ prevArg, currArg ] ) # save bad arguments as a list

    # TODO: check for empty params

  # -------------------------------------------------------------- #

  # check if any bad inputs collected
  flag = False
  for b in badInputs :
    if len(badInputs[b]) > 0 :
      flag = True

  # check results
  if noDedFile or (not nodesSpecified) or flag :
    msg                 = "\n"

    print badInputs

    # check for ded files
    if noDedFile :
      msg += "No Dedalus file(s) provided.\n"

    # check if node parameters specified
    elif not nodesSpecified :
      msg += """    Invalid input : comma-separated node list required.\n \
                   Please provide '-n <value>'. See usage for details.\n"""

    # check for all other param errors
    for k in badInputs :
      currBadInputList = badInputs[k]

      if k == "invalidDedFile" :
        for i in currBadInputList :
          badfile = i[0]
          msg += "    Input Dedalus file does not exist : " + badfile + "\n"

      elif k == "negValue" :
        for i in currBadInputList :
          msg += "    Input value is invalid : negative value : " + str(i) + "\n"

      elif k == "invalidNodeList" :
        for i in currBadInputList :
          msg += "    Input value is invalid : invalid node list: " + str(i) + """\n \
                                       comma-separated node list required.\n \
                                       Please provide '-n <value>'. See usage for details.\n"""

      elif k == "valueTypeError" :
        for i in currBadInputList :
          msg += "    Input value is invalid : value not an integer : " + str(i) + "\n"

      elif k == "invalidInput" :
        for i in currBadInputList :
          msg += "    Invalid input : " + str(i) + " not a valid option\n"

      elif k == "invalidSolver" :
        for i in currBadInputList :
          msg += "    Invalid solver : " + str(i) + """" not a valid solver\n \
                    valid solvers are """ + str(validSolverList) + "\n"

      elif k == "invalidStrategy" :
        for i in currBadInputList :
          msg += "    Invalid strategy : " + str(i) + " not a valid strategy\n \
                        valid strategies are """ + str(validStrategyList) + "\n"

      elif k == "missingInput" :
        for i in currBadInputList :
          msg += "    Missing input for : " + str(i)

    sys.exit( "> ERROR (caught in sanityCheck.py) : " + 
              msg + "\n" + 
              messages.LDFI_ParamInputError() + 
              "\nAborting ..." )

#########
#  EOF  #
######### 
