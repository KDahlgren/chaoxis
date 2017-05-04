#!/usr/bin/env python

'''
Test_FactNode.py
  Defines unit tests for FactNode.py from src/derivation/.
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


###############################
# Temp Classes for unitTests  #
###############################
class FactNodeTestFuncObj(FactNode.FactNode) :
  def __init__(self):
    self.isNeg = None
    self.results = []
    self.triggerRecord = []
    self.name = None
    self.record = []


####################
#  TEST FACT NODE  #
####################
class Test_FactNode( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_Fact( self ) :
    testFactNode = FactNode.FactNode(1,True,[ "1","2","3","4"], [[["1","2"],"2","3"],["1","2"]], "Test")
    self.assertTrue( testFactNode )


  #########
  #  STR  #
  #########
  def test_str_Fact( self ) :
    testFactNode = FactNodeTestFuncObj()
    testFactNode.isNeg = True
    testFactNode.name = "Test"
    self.assertTrue(testFactNode.__str__()=="fact-> _NOT_ Test([])")
    testFactNode.isNeg=False
    self.assertTrue(testFactNode.__str__()=="fact-> Test([])")


  #####################
  #  EXTRACT TRIGGER  #
  #####################
  def test_extractTrigger_Fact( self ) :
    testFactNode = FactNodeTestFuncObj()
    testFactNode.results = [[["1","2"],"2","3"],["1","2"]]
    testFactNode.name = 0
    testFactNode.record = [ "1","2","3","4"]
    self.assertTrue(testFactNode.extractTrigger()==["1","2"])
    testFactNode.name = 1
    self.assertTrue(testFactNode.extractTrigger()==["1"])


  ###########################
  #  VERIFY TRIGGER RECORD  #
  ###########################
  def test_verifyTriggerRecord_Fact( self ) :
    testFactNode = FactNodeTestFuncObj()
    testFactNode.results = [[["5","4"],"3","2"],["1","0"]]
    testFactNode.name = 1
    testFactNode.triggerRecord='1'
    self.assertTrue(testFactNode.verifyTriggerRecord())
    testFactNode.triggerRecord='2'
    self.assertFalse(testFactNode.verifyTriggerRecord())


#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
    unittest.main( verbosity=2 )


#########
#  EOF  #
#########
