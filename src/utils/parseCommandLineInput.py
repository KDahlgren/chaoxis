#!/usr/bin/env python

'''
parseCommandLineInput.py
   Use argparse to cleanly extract arguments provided
   at the commandline.
'''

import argparse, os, sys

##############################
#  PARSE COMMAND LINE INPUT  #
##############################
def parseCommandLineInput( ) :
  argDict = {}  # empty dict

  parser = argparse.ArgumentParser()

  # define all possible arguments here
  parser.add_argument("-t", "--EOT", type=int, help="end of time (default 3)", default = 3)
  parser.add_argument("-ff", "--EFF", type=int, help="end of finite failures (default 2)", default = 2)
  parser.add_argument("-f", "--file", help="input dedalus file (1 minimum required)", required=True) 
  parser.add_argument("-s", "--settings", help="input the complete path to a settings file\n(default = " + os.getcwd()+"/settings.txt" + ")", default=os.getcwd()+"/settings.txt" ) 
  parser.add_argument("-c", "--crashes", type=int, help="number of crash failures (default 0)", default = 0)
  parser.add_argument("-n", "--nodes", type=str, help="a comma-separated set of nodes indicating an all-to-all topology (optionally specify topology facts in input file(s))")
  parser.add_argument("--solver", type=str,  choices=['z3', 'sat4j', 'ilp'], help="the solver to use")
  parser.add_argument("--evaluator", type=str,  choices=['c4', 'pyDatalog'], help="the evaluator to use", default = "pyDatalog")
  parser.add_argument("--strategy", choices=['sat', 'random', 'pcausal'], help="the search strategy")
  parser.add_argument("--use-symmetry", help="use symmetry to skip equivalent failure scenarios", action="store_true")
  parser.add_argument("--prov-diagrams", help="generate provenance diagrams for each execution", action="store_true")
  parser.add_argument("--disable-dot-rendering", help="disable automatic rendering of `dot` diagrams", action="store_true")
  parser.add_argument("--find-all-counterexamples", help="continue after finding the first counterexample", action="store_true")
  parser.add_argument("--negative-support", help="Negative support.  Slow, but necessary for completeness", action="store_true")

  args = parser.parse_args()

  # collect arguments and values in a dictionary
  for a in vars(args) :
    if a == 'nodes' :
      try :
        argDict[a] = getattr(args, a).split(',')
      except :
        argDict[a] = []
    else :
      argDict[a] = getattr(args, a)

  return argDict

#########
#  EOF  #
#########
