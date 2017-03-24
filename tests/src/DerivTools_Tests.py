#!/usr/bin/env python

'''
DerivTools_Tests.py
  Defines unit tests for derivTools.
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

from derivTools import Node, FactNode
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
class DerivTools_Tests( unittest.TestCase ) :
  
##########
# NODE   # 
##########
  def test__Class__Node( self ) :
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

  def test__derivTools( self ) :
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
