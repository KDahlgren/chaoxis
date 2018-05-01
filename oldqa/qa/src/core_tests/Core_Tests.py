#!/usr/bin/env python

'''
Core_Tests.py
  Defines unit tests for core.
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


from dedt  import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import tools

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../../qa")


################
#  CORE TESTS  #
################
class Core_Tests( unittest.TestCase ) :

  ##########################
  #  INSTANTIATE LDFICORE  #
  ##########################
  #

  #############
  #  ATTRIBS  #
  #############
  def test_LDFICoreAttribs_dedt( self ) :
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
