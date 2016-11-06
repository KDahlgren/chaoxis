#!/usr/bin/env python

'''
Dedc_Tests.py
  Defines unit tests for dedc.
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
testPath = os.path.abspath(__file__+"/../../../tests")


from dedc import dedc, dedalusParser, clockRelation

# ------------------------------------------------------ #


################
#  DEDC TESTS  #
################
class Dedc_Tests( unittest.TestCase ) :

  def test_dedToIR_dedc( self ) :
    return None

  def test_IRToClock_dedc( self ) :
    return None

  def test_ClockToDatalog_dedc( self ) :
    return None

  def test_runCompiler_dedc( self ) :
    return None

  def test_compileDedalus_dedc( self ) :
    
  
    return None
    
########################
#  DEDALUSPARSER TESTS  #
#########################
  def test_cleanResult_dedalusParser(self):
    inputArg  = ('node', '(', 'Node', ',', ' ', 'Neighbor', ')', ';')
    outputResult = ['node', '(', 'Node', ',', ' ', 'Neighbor', ')', ';']
    self.assertEqual(dedalusParser.cleanResult(inputArg),outputResult)

  def test_parse_dedalusParser(self):
    #test detecting facts
    inputArg  = "watch('test', 'test')@1;"
    outputResult = "fact"
    self.assertEqual(dedalusParser.parse(inputArg)[0],outputResult)
    
    #test detecting rules
    inputArg  = "node(Node, Neighbor)@next :- node(Node, Neighbor);"
    outputResult = "rule"
    self.assertEqual(dedalusParser.parse(inputArg)[0],outputResult)
    
    #test detecting improper dedalus
    inputArg  = "improper dedalus"
    outputResult = None
    self.assertEqual(dedalusParser.parse(inputArg),outputResult)
        
    inputArg  = "improper ; dedalus"
    with self.assertRaises(SystemExit) as cm:
        dedalusParser.parse(inputArg)
    self.assertIn("ERROR",cm.exception.code)
        
    inputArg  = "'improper' :- 'dedalus' :- ;"
    with self.assertRaises(SystemExit) as cm:
      dedalusParser.parse(inputArg)
    self.assertIn("ERROR",cm.exception.code)

  def test_parseDedalus_dedalusParser(self): 
    #testing file parsing
    inputArg  = testPath+"\_testfiles\_testSingleLine.ded"
    outputResult = [('fact', ['node', '(', '"', 'a', '"', ',', ' ',\
    '"', 'b', '"', ')', '@', '1', ';'])]
    self.assertEqual(dedalusParser.parseDedalus(inputArg),outputResult)
    
    inputArg  = testPath+"\_testfiles\_testComments.ded"
    outputResult = []
    self.assertEqual(dedalusParser.parseDedalus(inputArg),outputResult)
     
    inputArg  = "nonexistentfile.ded"
    with self.assertRaises(SystemExit) as cm:
      dedalusParser.parseDedalus(inputArg)
    self.assertIn("ERROR",cm.exception.code)

########################
#  CLOCKRELATION TESTS  #
#########################
  def test_initClockRelation_clockRelation(self):
    return None
    
  def test_buildClockRelation_clockRelation(self):
    return None
    
########################
#  DEDALUSREWRITER TESTS  #
#########################
  def test_clean_dedalusRewriter(self):
    return None 
    
  def test_ruleDump_dedalusRewriter(self):
    return None  
    
  def test_getDeductiveRuleIDs_dedalusRewriter(self):
    return None 
    
  def test_getInductiveRuleIDs_dedalusRewriter(self):
    return None     

  def test_getAsynchronousRuleIDs_dedalusRewriter(self):
    return None  
    
  def test_getSubgoalsIDs_dedalusRewriter(self):
    return None   

  def test_getSubgoalAtts_dedalusRewriter(self):
    return None
    
  def test_rewriteDeductive_dedalusRewriter(self):
    return None 
   
  def test_rewriteInductive_dedalusRewriter(self):
    return None

  def test_rewriteAsynchronous_dedalusRewriter(self):
    return None
    
  def test_rewriteDedalus_dedalusRewriter(self):
    return None
    
##############################
#  PROVENANCEREWRITER TESTS  #
##############################
  def test_aggRuleProv_provenanceRewriter(self):
    return None 
    
  def test_getProv_provenanceRewriter(self):
    return None  
    
  def test_rewriteProvenance_provenanceRewriter(self):
    return None  
    
    
#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
    dedalusParser.parse("node(Node, Neighbor)@next :- node(Node, Neighbor);")
    unittest.main( verbosity=2 )


#########
#  EOF  #
#########
