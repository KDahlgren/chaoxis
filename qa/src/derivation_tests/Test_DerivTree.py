#!/usr/bin/env python

'''
Test_DerivTree.py
  Defines unit tests for DerivTree.py from src/derivation/.
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


#####################
#  TEST DERIV TREE  #
#####################
class Test_DerivTree( unittest.TestCase ) :


  ####################
  #  IS FINAL STATE  #
  ####################
  def isFinalState( self ) :
    return None


  #############
  #  IS LEAF  #
  #############
  def isLeaf( self ) :
    return None


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor__DerivTree( self ) :
    return None


  #########################
  #  GENERATE DERIV TREE  #
  #########################
  def test_generateDerivTree_DerivTree( self ) :
    return None


  ##################
  #  GET TOPOLOGY  #
  ##################
  def test_getTopology_DerivTree( self ) :
    return None

  #################
  #  ERROR MSG 1  #
  #################
  def test_errorMsg1_DerivTree( self ) :
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
