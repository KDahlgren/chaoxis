#!/usr/bin/env python

'''
Test_provTools.py
  Defines unit tests for provTools.py from src/derivation/.
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
#  TEST PROV TOOLS  #
#####################
class Test_provTools( unittest.TestCase ) :

  #################
  #  CREATE NODE  #
  #################
  def test_createNode_provTools( self ) :
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
