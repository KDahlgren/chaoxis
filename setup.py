#!/usr/bin/env python

import os, sys

# TODO: place magical installation code here

print "Running pyLDFI setup with : \n" + str(sys.argv)

if "c4" in sys.argv :
  print "Installing C4 Datalog evaluator ... "
  os.system( "make" )
  print "... Done installing C4 Datalog evaluator"
elif "pyDatalog" in sys.argv :
  print "Using pyDatalog Datalog evaluator."
else :
  print "Using pyDatalog Datalog evaluator."
