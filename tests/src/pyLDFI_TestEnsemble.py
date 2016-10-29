#!/usr/bin/env python

'''
pyLDFI_TestEnsemble.py
  Primary file driving the execution of the initial
  unit test framework.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
#packagePath  = os.path.abspath( __file__ + "/../../../src" )
#sys.path.append( packagePath )

from Utils_Tests import Utils_Tests
from Dedc_Tests  import Dedc_Tests
#from DerivTools_Tests import DerivTools_Tests
#from Evaluators_Tests import Evaluators_Tests
#from Solvers_Tests import Solvers_Tests
#from VizTools_Tests import VizTools_Tests
# ------------------------------------------------------ #

#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == "__main__" :

  print "*****************************************************"
  print
  print "Launching pyLDFI_TestEnsemble ..."

  print "\n\n******************"
  print ">> Utils_Tests"
  suite = unittest.TestLoader().loadTestsFromTestCase( Utils_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "\n\n******************"
  print ">> Dedc_Tests"
  suite = unittest.TestLoader().loadTestsFromTestCase( Dedc_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "\n\n******************"
  print ">> DerivTools_Tests"
  print "\n\n******************"
  print ">> Evaluators_Tests"
  print "\n\n******************"
  print ">> Solvers_Tests"
  print "\n\n******************"
  print ">> VizTools_Tests"

  print "*****************************************************"

#########
#  EOF  #
#########
