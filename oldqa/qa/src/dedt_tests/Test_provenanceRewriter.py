#!/usr/bin/env python

'''
Test_provenanceRewriter.py
  Defines unit tests for provenanceRewriter.py from src/dedt/.
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


##############################
#  TEST PROVENANCE REWRITER  #
##############################
class Test_provenanceRewriter( unittest.TestCase ) :

  ###################
  #  AGG RULE PROV  #
  ###################
  def test_aggRuleProv_provenanceRewriter(self):
    return None


  ##############
  #  GET PROV  #
  ##############
  def test_getProv_provenanceRewriter(self):
    return None


  ########################
  #  REWRITE PROVENANCE  #
  ########################
  def test_rewriteProvenance_provenanceRewriter(self):
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
