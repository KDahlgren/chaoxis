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
  def test__evalTools__bugFreeExecution( self ) :
    results = {"pre":[[1,"2","A"]],"post":[[1,"2","B"]]}
    eot = 3
    executionStatus = ""
    #Check 0:
    with self.assertRaises(SystemExit) as cm:
      evalTools.bugFreeExecution(results, eot, executionStatus)
    self.assertFalse(cm.exception==None)
   
    #Check 1:
    results = {"pre":[[1,"2","3"]],"post":[[1,"2","B"]]}
    with self.assertRaises(SystemExit) as cm:
      evalTools.bugFreeExecution(results, eot, executionStatus)
    self.assertFalse(cm.exception==None)
    
    #Check 2:
    results = {"pre":[[1,"2","4"]],"post":[[1,"2","4"]]}
    check=evalTools.bugFreeExecution(results, eot, executionStatus)

    self.assertTrue(check[1]=="post contains no eot data")
    
    #Check 3:
    results = {"pre":[[1,"2","3"]],"post":[[1,"2","4"]]}
    check=evalTools.bugFreeExecution(results, eot, executionStatus)
    self.assertTrue(check[1]== "eot tuples exist in pre, but not in post")
    
    results = {"pre":[[1,"2","3"]],"post":[[1,"2","3"]]}
    executionStatus = "noMoreEOTPostRecords"
    check=evalTools.bugFreeExecution(results, eot, executionStatus)
    self.assertTrue(check[1]== "noMoreEOTPostRecords")
    
    executionStatus = "exhaustedClockOnlySolns"
    check=evalTools.bugFreeExecution(results, eot, executionStatus)
    self.assertTrue(check[1]== "exhaustedClockOnlySolns")
    
    
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
