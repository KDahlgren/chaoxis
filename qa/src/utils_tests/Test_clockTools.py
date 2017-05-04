#!/usr/bin/env python

'''
Test_clockTools.py
  Defines unit tests for clockTools.py from utils/.
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

######################
#  TEST CLOCK TOOLS  #
######################
class Test_clockTools( unittest.TestCase ) :


  #################################
  #  ADD CLOCK SUBGOAL DEDUCTIVE  #
  #################################
  def test_addClockSubgoal_deductive_clockTools( self ) :
    return None


  #################################
  #  ADD CLOCK SUBGOAL INDUCTIVE  #
  #################################
  def test_addClockSubgoal_inductive_clockTools( self ) :
    return None


  #############################
  #  ADD CLOCK SUBGOAL ASYNC  #
  #############################
  def test_addClockSubgoal_async_clockTools( sefl) :
    return None


#########
#  EOF  #
#########
