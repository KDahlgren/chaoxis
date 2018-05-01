#!/usr/bin/env python

'''
Test_extractors.py
  Defines unit tests extractors.py for utils/.
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

#####################
#  TEST EXTRACTORS  #
#####################
class Test_extractors( unittest.TestCase ) :


  ##################
  #  IS LAST ITEM  #
  ##################
  def test_isLastItem_extractors( self ) :
    self.assertTrue(extractors.isLastItem(9,10)==True)
    self.assertTrue(extractors.isLastItem(8,10)==False)


  #############################
  #  EXTRACT ADDITIONAL ARGS  #
  #############################
  def test_extractAdditionalArgs_extractors( self ) :
    inputArg  = [ 'notin', 'node', '(', 'Node', ',', 'Neighbor', ')' ]
    outputResult = ['notin']
    self.assertEqual( extractors.extractAdditionalArgs( inputArg ), outputResult )


  ##################
  #  EXTRACT GOAL  #
  ##################
  def test_extractGoal_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next' ]
    self.assertEqual( extractors.extractGoal( inputArg ), outputResult )


  ############
  #  IS EQN  #
  ############
  def test_isEqn_extractors( self ) :
    testString = "Hello World!"
    testArr = [ "1+1", "45-asd", "   *", "asdf/", ">1", "2<", "<=",\
    ">=", "5==5", "2345!=965" ]
    self.assertTrue(extractors.isEqn(testString)==False)
    for item in testArr:
      self.assertTrue(extractors.isEqn(item)==True)


  ######################
  #  EXTRACT EQN LIST  #
  ######################
  def test_extractEqnList_extractors( self ) :
    return None


  ##########################
  #  EXTRACT SUBGOAL LIST  #
  ##########################
  def test_extractSubgoalList_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')' ]
    outputResult = ['node(Node,Neighbor)']
    self.assertEqual( extractors.extractSubgoalList( inputArg ), outputResult )


  ################
  #  BODY PARSE  #
  ################
  def test_bodyParse_extractors( self ) :
    return None


  ############
  #  HAS OP  #
  ############
  def test_hasOp_extractors( self ) :
    testString = "Hello World!"
    testArr = [ "1+1", "45-asd", "   *", "asdf/", ">1", "2<", "<=",\
    ">=", "5==5", "2345!=965" ]
    self.assertTrue(extractors.hasOp(testString)==False)
    for item in testArr:
      self.assertTrue(extractors.hasOp(item)==True)


  ######################
  #  EXTRACT TIME ARG  #
  ######################
  def test_extractTimeArg_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next' ]
    outputResult = "next"
    self.assertEqual( extractors.extractTimeArg( inputArg ), outputResult )


  ######################
  #  EXTRACT ATT LIST  #
  ######################
  def test_extractAttList_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ 'Node', 'Neighbor' ]
    self.assertEqual( extractors.extractAttList( inputArg ), outputResult )


  ##########################
  #  EXTRACT SUBGOAL NAME  #
  ##########################
  def test_extractSubgoalName_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = ["node"]
    self.assertEqual( extractors.extractSubgoalName( inputArg ), outputResult )


  ##################
  #  EXTRACT NAME  #
  ##################
  def test_extractName_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = "node"
    self.assertEqual( extractors.extractName( inputArg ), outputResult )



#########
#  EOF  #
#########
