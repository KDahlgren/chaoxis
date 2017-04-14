#!/usr/bin/env python

'''
Utils_Tests.py
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

from utils import clockTools, dumpers, extractors, tools, parseCommandLineInput
# ------------------------------------------------------ #

################
#  UNIT TESTS  #
################
class Utils_Tests( unittest.TestCase ) :

  # ///////////////////////////////////////////////// #
  #                   CLOCK TOOLS                     #
  # ///////////////////////////////////////////////// #

  def test_addClockSubgoal_deductive_clockTools( self ) :
    return None

  def test_addClockSubgoal_inductive_clockTools( self ) :
    return None

  def test_addClockSubgoal_async_clockTools( self ) :
    return None


  # ///////////////////////////////////////////////// #
  #                     DUMPERS                       #
  # ///////////////////////////////////////////////// #

  def test_ruleDump_dumpers( self ) :
    return None

  def test_factDump_dumpers( self ) :
    return None

  def test_clockDump_dumpers( self ) :
    return None

  def test_reconstructRule_dumpers( self ) :
    return None


  # ///////////////////////////////////////////////// #
  #                    EXTRACTORS                     #
  # ///////////////////////////////////////////////// #

  def test_extractAdditionalArgs_extractors( self ) :
    inputArg  = [ 'notin', 'node', '(', 'Node', ',', 'Neighbor', ')' ]
    outputResult = ['notin']
    self.assertEqual( extractors.extractAdditionalArgs( inputArg ), outputResult )

  def test_extractGoal_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next' ]
    self.assertEqual( extractors.extractGoal( inputArg ), outputResult )

  def test_extractSubgoalList_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', ',', 'Neighbor', ')' ]
    outputResult = [ 'node(Node,Neighbor)' ]
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
    outputResult = ["node"]
    self.assertEqual( extractors.extractSubgoalName( inputArg ), outputResult )
    
    inputArg  = [ 'notin', 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = ["notin", "node"]
    self.assertEqual( extractors.extractSubgoalName( inputArg ), outputResult )

  def test_extractName_extractors( self ) :
    inputArg  = [ 'node', '(', 'Node', ',', 'Neighbor', ')', ';' ]
    outputResult = "node"
    self.assertEqual( extractors.extractName( inputArg ), outputResult )


  # ///////////////////////////////////////////////// #
  #                      TOOLS                        #
  # ///////////////////////////////////////////////// #

  def test_getID_tools( self ) :
    outputResult = 16
    self.assertEqual( len( tools.getID( ) ), outputResult )

  def test_getRandomAttName_tools( self ) :
    outputResult = 16
    self.assertEqual( len( tools.getRandomAttName() ), 16 )

  def test_getEvalResults_file_c4_tools( self ) :
    return None

  def test_checkIfRewrittenAlready_tools( self ) :
    return None

  def test_checkParentheses_tools( self ) :
    inputArg  = "node(Node, Neighbor)@next :- node(Node, Neighbor) ;"
    outputResult = True
    self.assertEqual( tools.checkParentheses( inputArg ), outputResult )

  def test_toAscii_list_tools( self ) :
    return None

  def test_toAscii_multiList_tools( self ) :
    return None

  def test_toAscii_str_tools( self ) :
    return None

  def test_skip_tools( self ) :
    return None

  def test_getAllIncludedFiles_tools( self ) :
    return None

  def test_combineLines_tools( self ) :
    return None

  def test_attSearchPass2_tools( self ) :
    return None

  def test_isFact_tools( self ) :
    return None

  def test_checkDataTypes_tools( self ) :
    return None

  def test_isString_tools( self ) :
    return None

  def test_isInt_tools( self ) :
    return None

  def test_getVarType_tools( self ) :
    return None

  def test_containsEqn_tools( self ) :
    return None

  # ///////////////////////////////////////////////// #
  #              PARSE COMMAND LINE INPUT             #
  # ///////////////////////////////////////////////// #

  def test_parseCommandLineInput_parseCommandLineInput( self ) :
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
