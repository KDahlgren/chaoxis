#!/usr/bin/env python

# contains ~*~ magic ~*~ installation code.

import os, sys


##########
#  MAIN  #
##########
def main() :
  print "Running pyLDFI setup with args : \n" + str(sys.argv)

  # clean any existing libs
  os.system( "make clean" )

  # download submodules
  os.system( "make get-submodules" )

  # ---------------------------------------------- #

  os.system( "make sniper" )


###################
#  CHECK PY DEPS  #
###################
# check python package dependencies
def checkPyDeps() :

  print "*******************************"
  print "  CHECKING PYTHON DEPENDECIES  "
  print "*******************************"

  # argparse
  import argparse
  if argparse.__name__ :
    print "argparse...verified"
  
  # pyparsing
  import pyparsing
  if pyparsing.__name__ :
    print "pyparsing...verified"
  
  # sqlite3
  import sqlite3
  if sqlite3.__name__ :
    print "sqlite3...verified"
  
  # pydatalog
  #import pyDatalog
  #if pyDatalog.__name__ :
  #  print "pyDatalog...verified"
  
  # pydot
  import pydot
  if pydot.__name__ :
    print "pydot...verified"
  
  # mpmath
  import mpmath
  if mpmath.__name__ :
    print "mpmath...verified"
  
  # sympy
  import sympy
  if sympy.__name__ :
    print "sympy...verified"

  # pycosat
  import pycosat
  if pycosat.__name__ :
    print "pycosat...verified"

  print "All python dependencies installed! Yay! =D"
  print "*******************************"
  print "*******************************"

  return None


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
if __name__ == "__main__" :
  checkPyDeps()
  main()


#########
#  EOF  #
#########
