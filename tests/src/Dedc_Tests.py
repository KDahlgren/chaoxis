#!/usr/bin/env python

'''
Dedc_Tests.py
  Defines unit tests for dedc.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest,sqlite3

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

  def test_createDedalusIRTables_dedc( self ) : 
    #testing set up
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    
    #checks if it runs through function withou error
    self.assertTrue(dedc.createDedalusIRTables(cursor)==None)
    
    #checks if the tables are actually created
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Fact'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='FactAtt'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Rule'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GoalAtt'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Subgoals'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SubgoalAddArgs'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Equation'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Clock'").fetchone()==None)
  
    #clean up testing
    IRDB.close()
    os.remove( testDB )
    
    
  def test_dedToIR_dedc( self ) :
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    dedc.createDedalusIRTables(cursor)
    
    #throws error for nonexistent file
    inputfile = "./nonexistentfile.ded"
    with self.assertRaises(SystemExit) as cm:
        dedc.dedToIR(inputfile,cursor)
    self.assertIn("ERROR",cm.exception.code)
    
    #returns a result
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    outputResult = None
    self.assertFalse(dedc.dedToIR(inputfile,cursor)==outputResult)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )

  def test_starterClock_dedc( self ) :
    #tested in clockRelation tests below
    return None
    

  def test_rewrite_dedc( self ) :
    #tested in dedalusRewriter and
    #provenanceRewriter below
    return None

  def test_runCompiler_dedc( self ) :
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    dedc.createDedalusIRTables(cursor)
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2}
    
    #returns a result
    outputResult = None
    self.assertFalse(dedc.runCompiler(cursor,inputfile,inputArg,None)==outputResult)
    c4file = dedc.runCompiler(cursor,inputfile,inputArg,None)
    
     #clean up testing
    IRDB.close()
    os.remove( testDB )
    os.remove(c4file)
    
  def test_compileDedalus_dedc( self ) :
  
    #throw error when file not found (currently leaves behind the DB file)
    '''inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': './nonexistentfile.ded', 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2}
    with self.assertRaises(SystemExit) as cm:
        dedc.compileDedalus(inputArg)
    self.assertIn("ERROR",cm.exception.code)'''
    
    #returns a result
    inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2}
    outputResult = None
    self.assertFalse(dedc.compileDedalus(inputArg)==outputResult)
    
    
    
#########################
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
    inputArg  = testPath+"/testfiles/testSingleLine.ded"
    outputResult = [('fact', ['node', '(', '"a","b"', ')', '@', '1'])]
    self.assertEqual(dedalusParser.parseDedalus(inputArg),outputResult)
    
    inputArg  = testPath+"/testfiles/testComments.ded"
    outputResult = []
    self.assertEqual(dedalusParser.parseDedalus(inputArg),outputResult)
     
    inputArg  = "nonexistentfile.ded"
    with self.assertRaises(SystemExit) as cm:
      dedalusParser.parseDedalus(inputArg)
    self.assertIn("ERROR",cm.exception.code)

#########################
#  CLOCKRELATION TESTS  #
#########################
  def test_initClockRelation_clockRelation(self):
    return None
    
  def test_buildClockRelation_clockRelation(self):
    return None
    
###########################
#  DEDALUSREWRITER TESTS  #
###########################
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
    unittest.main( verbosity=2 )


#########
#  EOF  #
#########
