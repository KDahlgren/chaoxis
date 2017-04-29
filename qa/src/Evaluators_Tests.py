#!/usr/bin/env python

'''
Evaluators_Tests.py
  Defines unit tests for evaluators.
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

testPath = os.path.abspath(__file__+"/../../../qa")
from evaluators import c4_evaluator, evalTools
# ------------------------------------------------------ #


######################
#  EVALUATORS TESTS  #
######################
class Evaluators_Tests( unittest.TestCase ) :


##############
# Eval Tools #
##############
  def test__evalTools__bugConditions( self ) :
    eot = 3
    executionStatus = ""

    # CLOCK FACTS MUST BE INTEGERS
    #results = {"pre":[[1,"2","A"]],"post":[[1,"2","B"]]}
    #with self.assertRaises(SystemExit) as cm:
    #  evalTools.bugConditions(results, eot)
    #self.assertFalse(cm.exception==None)
   
    # EMPTY PRE AND POST
    results = {"pre":[],"post":[]}
    check=evalTools.bugConditions(results, eot)
    self.assertTrue(check =="NoCounterexampleFound")

    # VACUOUSLY CORRECT
    results = {"pre":[[1,"2","2"]],"post":[[1,"2","2"]]}
    check=evalTools.bugConditions(results, eot)
    self.assertTrue(check == "NoCounterexampleFound")

    # COUNTER EXAMPLE
    results = {"pre":[[1,"2","3"]],"post":[[1,"2","2"]]}
    check=evalTools.bugConditions(results, eot)
    self.assertTrue(check == "FoundCounterexample")



#################
#  c4_evaluator #
#################
  def test__c4_evaluator__cleanTableStr( self ) :
    test = "th,is,,,,,i,s,,,,a,,,test,,,,,"
    self.assertTrue(c4_evaluator.cleanTableStr(test)=="th,is,,i,s,a,test")
    
  def test__c4_evaluator__getTables(self):
    pathString = "fakepath"	
    with self.assertRaises(SystemExit) as cm:
      c4_evaluator.getTables(pathString)
    self.assertFalse(cm.exception==None) 

    pathString = testPath  + "/testfiles/tableListStr.data"
    tableListStr ="node,log,log,log,missing_log,pre,post,\
    node_provpeoppjazkjosbhdc,log_provrviqfdywigwycwfq,\
    log_provncajgdrtwklgyzde,log_provoiaxlftqpnlkpjag,\
    missing_log_provqemllvdeknisseki,pre_provklfbtamenwjruhph,\
    post_provbkesmzuhxpevizwx,bcast,clock"
    self.assertTrue(str(c4_evaluator.getTables(pathString)==tableListStr))
    
  def test__c4_evaluator_runC4_directly(self):
    table_path = testPath  + "/testfiles/tableListStr.data"
    c4_file_path = testPath  + "/testfiles/c4program.olg"
    savepath = testPath  + "/testfiles/" 
    failpath = ""
    with self.assertRaises(SystemExit) as cm:
      c4_evaluator.runC4_directly(failpath, table_path, savepath)
    self.assertFalse(cm.exception==None) 

    
    
#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
  unittest.main( verbosity=2 )


#########
#  EOF  #
#########
