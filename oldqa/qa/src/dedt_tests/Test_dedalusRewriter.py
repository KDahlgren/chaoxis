#!/usr/bin/env python

'''
Test_dedalusRewriter.py
  Defines unit tests for dedalusRewriter.py from src/dedt/.
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


###########################
#  TEST DEDALUS REWRITER  #
###########################
class Test_dedalusRewriter( unittest.TestCase ) :

  ##################
  #  GET RULE IDS  #
  ##################
  #testing for the helper functions: getdeductiveRuleIDs,
  #getInductiveRuleIDs and getAsynchronousRuleIDs
  def test_getRuleIDs_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR(inputfile,cursor)
    
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getDeductiveRuleIDs(cursor)==None)
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getInductiveRuleIDs(cursor)==None)
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getAsynchronousRuleIDs(cursor)==None)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ######################
  #  GET SUBGOALS IDS  #  
  ######################
  def test_getSubgoalsIDs_dedalusRewriter(self):
    return None   


  #######################
  #  GET SUBGOALS ATTS  #
  #######################
  def test_getSubgoalAtts_dedalusRewriter(self):
    return None


  #######################
  #  REWRITE DEDUCTIVE  #
  #######################
  def test_rewriteDeductive_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR(inputfile,cursor)
    
    #runs through function to make sure it finishes without error
    self.assertTrue(dedalusRewriter.rewriteDeductive(cursor)==None)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB ) 


  #######################
  #  REWRITE INDUCTIVE  #
  #######################
  def test_rewriteInductive_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR(inputfile,cursor)
    
    #runs through function to make sure it finishes without error
    self.assertTrue(dedalusRewriter.rewriteInductive(cursor)==None)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB ) 


  ##########################
  #  REWRITE ASYNCHRONOUS  #
  ##########################
  def test_rewriteAsynchronous_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR(inputfile,cursor)
    
    #runs through function to make sure it finishes without error
    self.assertTrue(dedalusRewriter.rewriteAsynchronous(cursor)==None)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB ) 


  #####################
  #  REWRITE DEDALUS  #
  #####################
  def test_rewriteDedalus_dedalusRewriter(self):
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
