#!/usr/bin/env python

'''
Derivation_Tests.py
  Defines unit tests for derivation.
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
    


######################
#  DERIVTOOLS TESTS  #
######################


class Derivation_Tests( unittest.TestCase ) :
	
##########
# NODE   # 
##########
  def test__Class_Node( self ) :
    with self.assertRaises(TypeError) as cm:
      testNodeFail = Node.Node("Test","Test")
    self.assertFalse(cm.exception==None)
    
    testNode = Node.Node("Test",4,True,[1,2,3],"Test", "Test")
    self.assertTrue(testNode.treeType=="Test")
    self.assertTrue(testNode.name==4)
    self.assertTrue(testNode.isNeg==True)
    self.assertTrue(len(testNode.record)==3)
    self.assertTrue(testNode.results=="Test")
    self.assertTrue(testNode.cursor=="Test")
    
#############
# FactNode  #
#############
#depends on Node obj and tools
  def test_____str__FactNode(self):
    testFactNode = FactNodeTestFuncObj()
    testFactNode.isNeg = True
    testFactNode.name = "Test"
    self.assertTrue(testFactNode.__str__()=="fact-> _NOT_ Test([])")
    testFactNode.isNeg=False
    self.assertTrue(testFactNode.__str__()=="fact-> Test([])")
    
    
  def test__extractTrigger__FactNode(self):
    testFactNode = FactNodeTestFuncObj()
    testFactNode.results = [[["1","2"],"2","3"],["1","2"]]
    testFactNode.name = 0
    testFactNode.record = [ "1","2","3","4"]
    self.assertTrue(testFactNode.extractTrigger()==["1","2"])
    testFactNode.name = 1
    self.assertTrue(testFactNode.extractTrigger()==["1"])
    
  def test__verifyTriggerRecord__FactNode(self):
    testFactNode = FactNodeTestFuncObj()
    testFactNode.results = [[["5","4"],"3","2"],["1","0"]]
    testFactNode.name = 1
    testFactNode.triggerRecord='1'
    self.assertTrue(testFactNode.verifyTriggerRecord())
    testFactNode.triggerRecord='2'
    self.assertFalse(testFactNode.verifyTriggerRecord())
  	  
  def test__Class__FactNode(self):
    testFactNode = FactNode.FactNode(1,True,[ "1","2","3","4"], [[["1","2"],"2","3"],["1","2"]], "Test")
    self.assertTrue( testFactNode )

##############
#  Goal Node #
##############
  def test____str____GoalNode(self):
    return None
  
  def test__display__GoalNode(self):
    return None
    
  def test__getClockTriggerRecordList__GoalNode(self):
    return None
    
  def test__getAllIDPairs__GoalNode(self):
    return None
    
  def test__checkListEquality__GoalNode(self):
    return None
    
  def test__getGoalAttMaps__GoalNode(self):
    return None
    
  def test__mergeMaps__GoalNode(self):
    return None
  
  def test__getORID__GaolNode(self):
    return None
  
  def test__getAllTriggerRecords__GoalNode(self):
    return None
  
  def test__checkAgreement__GoalNode(self):
    return None
  
  def test__setDescendants__GoalNode(self):
    return None
    
  def test__spawnFact__GoalNode(self):
    return None
  
  def test__spawnRule__GoalNode(self):
    return None
  
  def test__Class__GoalNode(self):
    return None

###############
#  Rule Node  #
###############
  def test__Class__RuleNode(self):
    return None
  def test____str____RuleNode(self):
    return None
  def test__getFullMap__RuleNode(self):
    return None
  def test__getSubgoalInfo__RuleNode(self):
    return None
  def test__getSubgaolSeedRecords__RuleNode(self):
    return None
  def test__setDescendants__RuleNode(self):
    return None
  def test__spawnNode__RuleNode(self):
    return None
###############
#  ProvTools  #
###############
  def test__getOrigRID__ProvTools(self):
    return None
  def test__getPartialMatches__ProvTools(self):
    return None
  def test__createNode__ProvTools(self):
    return None
  def test__subAttMapping__ProvTools(self):
    return None
  def test__getSubAttMap__ProvTools(self):
    return None
  def test__getAttVal__ProvTools(self):
    return None
  def test__getGoalAttMap__ProvTools(self):
    return None
  def test__getFullCandidateProvRecords__ProvTools(self):
    return None
  def test__getSubgoals__ProvTools(self):
    return None
  def test__get_prov_rid_info__ProvTools(self):
    return None
  def test__checkEqaulity__ProvTools(self):
    return None

###############
#  Deriv Tree #
###############

def test__isFinalState__DerivTree(self):
  return None
  
def test__isLeaf__DerivTree(self):
  return None

def test__generateDerivTree__DerivTree(self):
  return None

def test__getTopology__DerivTree(self):
  return None
  
def test__errorMsg1__DerivTree(self):
  return None

def test__Class__DerivTree(self):
  return None


###############
#  Prov Tree  #
###############
 
#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
  unittest.main( verbosity=2 )


#########
#  EOF  #
#########
