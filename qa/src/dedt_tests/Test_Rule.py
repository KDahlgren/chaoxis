#!/usr/bin/env python

'''
Test_Rule.py
  Defines unit tests for Rule.py from src/dedt/.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )


from dedt import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import tools

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../../qa")


###############
#  TEST RULE  #
###############
class Test_Rule( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_Rule( self ) :
    return None


  ###################
  #  GET GOAL NAME  #
  ###################
  def test_getGoalName_Rule( self ) :
    return None


  ###################
  #  GET REWRITTEN  #
  ###################
  def test_getRewritten_Rule( self ) :
    return None


  #######################
  #  GET GOAL ATT LIST  #
  #######################
  def test_getGoalAttList_Rule( self ) :
    return None


  #######################
  #  GET GOAL TIME ARG  #
  #######################
  def test_getGoalTimeArg_Rule( self ) :
    return None


  ##########################
  #  GET SUBGOAL LIST STR  #
  ##########################
  def test_getSubgoalListStr_Rule( self ) :
    return None


  #######################################
  #  GET SUBGOAL LIST STR NO TIME ARGS  #
  #######################################
  def test_getSubgoalListStr_noTimeArgs_noAddArgs_Rule( self ) :
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
