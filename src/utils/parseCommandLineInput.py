#!/usr/bin/env python

##############################
#  PARSE COMMAND LINE INPUT  #
##############################
def parseCommandLineInput( argList ) :
  argDict = {} # empty dict

  numDedFiles = 0
  for i in range( 0, len(argList) ) :
    currArg = argList[i]            # current argument
    prevArg = ""                    # initialize empty
    key     = ""
    val     = ""

    if i > 0 :
      prevArg = argList[i-1]        # previous argument

    # check for ded files
    if ".ded" in currArg :
      key = "file" + str(numDedFiles)     # create unique key
      val = currArg
      numDedFiles = numDedFiles + 1  # increment ded file counter

    # check for solver
    elif '--solver' == prevArg :
      key = 'solver'
      val = currArg

    # check for strategy
    elif '--strategy' == prevArg :
      key = 'strategy'
      val = currArg

    # check for use symmetry
    elif '--use-symmetry' == prevArg :
      key = 'use-symmetry'
      val = currArg

    # check for prov diagrams
    elif '--prov-diagrams' == prevArg :
      key = 'prov-diagrams'
      val = currArg

    # check for disable dot rendering
    elif '--disable-dot-rendering' == prevArg :
      key = 'disable-dot-rendering'
      val = currArg

    # check for find all counterexamples
    elif '--find-all-counterexamples' == prevArg :
      key = 'find-all-counterexamples'
      val = currArg

    # check for negative support
    elif '--negative-support' == prevArg :
      key = 'negative-support'
      val = currArg

    else :
      # check for EOT
      if ('-t' == prevArg) or ('--EOT' == prevArg) :
        key = 'EOT'

      # check for EFF
      elif ('-f' == prevArg) or ('--EFF' == prevArg) :
        key = 'EFF'

      # check for crash info
      elif ('-c' == prevArg) or ('--crashes' == prevArg) :
        key = 'crashes'

      # check for node info
      elif ('-n' == prevArg) or ('-N' == prevArg) or ('--nodes' == prevArg) :
        key = 'nodes'

      # get value for key
      val = currArg

    if not (key == '') :    
      argDict[ key ] = val            # save to dict

  return argDict
