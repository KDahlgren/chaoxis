#!/usr/bin/env python

'''
Test_Fact.py
  Defines unit tests for Fact.py from src/dedt/.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )


from dedt import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import tools

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../../qa")


###############
#  TEST FACT  #
###############
class Test_Fact( unittest.TestCase ) :


  #################
  #  CONSTRUCTOR  #
  #################
  def test_constructor_Fact( self ) :
    return None


  ##############
  #  GET NAME  #
  ##############
  def test_getName_Fact( self ) :
    return None


  ##################
  #  GET ATT LIST  #
  ##################
  def test_getAttList_Fact( self ) :
    return None


  ##################
  #  GET TIME ARG  #
  ##################
  def test_getTimeArg_Fact( self ) :
    return None


  ###################
  #  SET FACT INFO  #
  ###################
  def test_setFactInfo_Fact( self ) :
    return None


  ##################
  #  SET ATT LIST  #
  ##################
  def test_setAttList_Fact( self ) :
    return None


  ###################
  #  SET ATT TYPES  #
  ###################
  def test_setAttTypes_Fact( self ) :
    return None


  ###################
  #  GET TYPE LIST  #
  ###################
  def test_getTypeList_Fact( self ) :
    return None


  #############
  #  DISPLAY  #
  #############
  def test_display_Fact( self ) :
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
