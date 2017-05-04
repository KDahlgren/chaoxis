#!/usr/bin/env python

'''
Test_GoalNode.py
  Defines unit tests for GoalNode.py from src/derivation/.
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


###############
#  TEST GOAL  #
###############
class Test_GoalNode( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_GoalNode( self ) :
    return None


  #########
  #  STR  #
  #########
  def test_str_GoalNode( self ) :
    return None


  #############
  #  DISPLAY  #
  #############
  def test_display_GoalNode( self ) :
    return None


  ###################
  #  GET CLOCK MAP  #
  ###################
  def test_getClockMap_GoalNode( self ) :
    return None


  ######################
  #  GET ALL ID PAIRS  #
  ######################
  def test_getAllIDPairs_GoalNode( self ) :
    return None


  #########################
  #  CHECK LIST EQUALITY  #
  #########################
  def test_checkListEquality_GoalNode( self ) :
    return None


  #######################
  #  GET GOAL ATT MAPS  #
  #######################
  def test_getGoalAttMaps_GoalNode( self ) :
    return None


  ################
  #  MERGE MAPS  #
  ################
  def test_mergeMaps_GoalNode( self ) :
    return None


  ################################################
  #  GET O(riginal Rule) G(oal) ATT(ribute) MAP  #
  ################################################
  def test_getOGattMap_GoalNode( self ) :
    return None


  ##############
  #  GET ORID  #
  ##############
  def test_getORID_GoalNode( self ) :
    return None


  #############################
  #  GET ALL TRIGGER RECORDS  #
  #############################
  def test_getAllTriggerRecords_GoalNode( self ) :
    return None


  #####################
  #  CHECK AGREEMENT  #
  #####################
  def test_checkAgreement_GoalNode( self ) :
    return None


  #####################
  #  SET DESCENDANTS  #
  #####################
  def test_setDescendants_GoalNode( self ) :
    return None


  ################
  #  SPAWN FACT  #
  ################
  def test_spawnFact_GoalNode( self ) :
    return None


  ################
  #  SPAWN RULE  #
  ################
  def test_spawnRule_GoalNode( self ) :
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
