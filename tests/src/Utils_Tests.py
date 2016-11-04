#!/usr/bin/env python

'''
PyLDFI_TestSuite_.py
  Defines unit tests for utils.
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

from utils import tools, extractors
# ------------------------------------------------------ #


################
#  UNIT TESTS  #
################
class Utils_Tests( unittest.TestCase ) :

  def test_getID_tools( self ) :
    outputResult = 16
    self.assertEqual( len( tools.getID( ) ), outputResult )

  def test_checkParentheses_tools( self ) :
    inputArg  = "node(Node, Neighbor)@next :- node(Node, Neighbor) ;"
    outputResult = True
    self.assertEqual( tools.checkParentheses( inputArg ), outputResult )

  def test_extractAdditionalArgs_extractors( self ) :
    inputArg  = [ 'notin', 'node', '(', 'Node', ',', 'Neighbor', ')' ]
    outputResult = ['notin']
    self.assertEqual( extractors.extractAdditionalArgs( inputArg ), outputResult )

  def test_extractGoal_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next' ]
    self.assertEqual( extractors.extractGoal( inputArg ), outputResult )

  def test_extractSubgoalList_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ [ 'node', '(', 'Node', ',', 'Neighbor', ')' ] ]
    self.assertEqual( extractors.extractSubgoalList( inputArg ), outputResult )

  def test_extractTimeArg_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next' ]
    outputResult = "next"
    self.assertEqual( extractors.extractTimeArg( inputArg ), outputResult )

  def test_extractAttList_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ 'Node', 'Neighbor' ]
    self.assertEqual( extractors.extractAttList( inputArg ), outputResult )

  def test_extractSubgoalName_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = "node"
    self.assertEqual( extractors.extractSubgoalName( inputArg ), outputResult )

  def test_extractName_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = "node"
    self.assertEqual( extractors.extractName( inputArg ), outputResult )

#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
  unittest.main( verbosity=2 )


#########
#  EOF  #
#########
