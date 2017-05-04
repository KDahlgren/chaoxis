#!/usr/bin/env python

'''
Test_ProvTree.py
  Defines unit tests for ProvTree.py from src/derivation/.
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
#  TEST PROV TREE  #
####################
class Test_ProvTree( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_ProvTree( self ) :
    return None


  ######################
  #  IS ULTIMATE GOAL  #
  ######################
  def test_isUltimateGoal_ProvTree( self ) :
    return None


  #############
  #  IS LEAF  #
  #############
  def test_isLeaf_ProvTree( self ) :
    return None


  #########################
  #  GENEARATE PROV TREE  #
  #########################
  def test_generateProvTree_ProvTree( self ) :
    return None


  ##################
  #  CREATE GRAPH  #
  ##################
  def test_createGraph_ProvTree( self ) :
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
