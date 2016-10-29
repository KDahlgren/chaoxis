#!/usr/bin/env python

'''
Dedc_Tests_.py
  Defines unit tests for dedc.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../../src" )
sys.path.append( packagePath )

from dedc import dedc, dedalusParser, clockRelation
# ------------------------------------------------------ #


################
#  DEDC TESTS  #
################
class Dedc_Tests( unittest.TestCase ) :

  def test_getID_dedc( self ) :
    outputResult = 16
    self.assertEqual( len( dedc.getID( ) ), outputResult )

  def test_dedToIR_dedc( self ) :
    return None

  def test_IRToClock_dedc( self ) :
    return None

  def test_ClockToDatalog_dedc( self ) :
    return None

  def test_runCompiler_dedc( self ) :
    return None

  def test_compileDedalus_dedc( self ) :
    return None

 
#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
  unittest.main( verbosity=2 )


#########
#  EOF  #
#########
