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
packagePath  = os.path.abspath( __file__ + "/../../src" )
sys.path.append( packagePath )

from Utils_Tests      import *
from Dedt_Tests       import *
from DerivTools_Tests import *
from Evaluators_Tests import *
from Solvers_Tests    import *
from VizTools_Tests   import * 
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
  suite = unittest.TestLoader().loadTestsFromTestCase( DerivTools_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "\n\n******************"
  print ">> Evaluators_Tests"
  suite = unittest.TestLoader().loadTestsFromTestCase( Evaluators_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "\n\n******************"
  print ">> Solvers_Tests"
  suite = unittest.TestLoader().loadTestsFromTestCase( Solvers_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "\n\n******************"
  print ">> VizTools_Tests"
  suite = unittest.TestLoader().loadTestsFromTestCase( VizTools_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "*****************************************************"

#########
#  EOF  #
#########
