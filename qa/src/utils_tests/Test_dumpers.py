#!/usr/bin/env python

'''
Test_dumpers.py
  Defines unit tests for dumpers.py from utils/.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )

from utils import tools, extractors, parseCommandLineInput

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../../qa")

##################
#  TEST DUMPERS  #
##################
class Test_dumpers( unittest.TestCase ) :


  ###############
  #  RULE DUMP  #
  ###############
  def test_ruleDump_dumpers( self ) :
    return None


  ###############
  #  FACT DUMP  #
  ###############
  def test_factDump_dumpers( self ) :
    return None


  ################
  #  CLOCK DUMP  #
  ################
  def test_clockDump_dumpers( self ) :
    return None


  ######################
  #  RECONSTRUCT RULE  #
  ######################
  def test_reconstructRule_dumpers( self ) :
    return None



#########
#  EOF  #
#########
