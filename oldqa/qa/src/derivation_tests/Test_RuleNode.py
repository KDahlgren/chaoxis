#!/usr/bin/env python

'''
Test_RuleNode.py
  Defines unit tests for RuleNode.py from src/derivation/.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, unittest
from StringIO import StringIO
# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../../src" )
sys.path.append( packagePath )

from derivation import Node, FactNode
# ------------------------------------------------------ #


####################
#  TEST RULE NODE  #
####################
class Test_RuleNode( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_RuleNode( self ) :
    return None


  #########
  #  STR  #
  #########
  def test_str_RuleNode( self ) :
    return None


  ##################
  #  GET FULL MAP  #
  ##################
  def test_getFullMap_RuleNode( self ) :
    return None


  ######################
  #  GET SUBGOAL INFO  #
  ######################
  def test_getSubgoalInfo_RuleNode( self ) :
    return None


  ##############################
  #  GET SUBGOAL SEED RECORDS  #
  ##############################
  def test_getSubgoalSeedRecords_RuleNode( self ) :
    return None


  #####################
  #  SET DESCENDANTS  #
  #####################
  def test_setDescendants_RuleNode( self ) :
    return None


  ################
  #  SPAWN NODE  #
  ################
  def test_spawnNode_RuleNode( self ) :
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
