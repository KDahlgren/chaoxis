#!/usr/bin/env python

'''
Dedt_Tests.py
  Defines unit tests for dedt.
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


from dedt import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import tools

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../qa")


################
#  DEDT TESTS  #
################
class Dedt_Tests( unittest.TestCase ) :

  # ///////////////////////////////////////////////// #
  #                       DEDT                        #
  # ///////////////////////////////////////////////// #

  def test_createDedalusIRTables_dedt( self ) : 
    #testing set up
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    
    #checks if it runs through function without error
    self.assertTrue(dedt.createDedalusIRTables(cursor)==None)
    
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
    
    
  def test_dedToIR_dedt( self ) :
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    
    #throws error for nonexistent file
    inputfile = "./nonexistentfile.ded"
    with self.assertRaises(SystemExit) as cm:
        dedt.dedToIR(inputfile,cursor)
    self.assertIn("ERROR",cm.exception.code)
    
    #runs through function to make sure it finishes without error
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    outputResult = None
    self.assertFalse(dedt.dedToIR(inputfile,cursor)==outputResult)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )

  def test_starterClock_dedt( self ) :
    #tested in clockRelation tests below
    return None
    
  def test_rewrite_dedt( self ) :
    #tested in dedalusRewriter and
    #provenanceRewriter below
    return None

  def test_runTranslator_dedt( self ) :
    #testing set up. runTranslator has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    
    #dependency
    dedt.createDedalusIRTables(cursor)
    
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2, 'evaluator': 'c4'}
    
    #runs through function to make sure it finishes without error
    outputResult = None
    evaluator    = "c4"
    self.assertFalse(dedt.runTranslator(cursor,inputfile,inputArg,None,evaluator)==outputResult)
    outpaths = dedt.runTranslator(cursor,inputfile,inputArg,None,evaluator)
    tables   = outpaths[0]
    c4file   = outpaths[1]

    #clean up testing
    IRDB.close()
    os.remove( testDB )
    if tables is not None:
      os.remove(tables)
    if c4file is not None:
      os.remove(c4file)
    
  def test_translateDedalus_dedt( self ) :
  
    #throw error when file not found (currently leaves behind the DB file)
    '''inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': './nonexistentfile.ded', 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2}
    with self.assertRaises(SystemExit) as cm:
        dedt.translateDedalus(inputArg)
    self.assertIn("ERROR",cm.exception.code)'''
    
    #returns a result
    inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2, 'evaluator': 'c4'}
    outputResult = None
    self.assertFalse(dedt.translateDedalus(inputArg)==outputResult)


  # ///////////////////////////////////////////////// #
  #                  DEDALUS PARSER                   #
  # ///////////////////////////////////////////////// #

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


  # ///////////////////////////////////////////////// #
  #                   CLOCK RELATION                  #
  # ///////////////////////////////////////////////// #

  def test_initClockRelation_clockRelation(self):
    #testing setup. initClockRelation has dependency
    #on createDedalusIRTables and dedToIR so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #Dependencies
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR( inputfile, cursor )
    
    #for saving the program clock output
    #to be used in comparison below
    clockRelation.CLOCKRELATION_DEBUG = True
    originalStdout                    = sys.stdout
    cmdResult                         = StringIO()
    fileResult                        = StringIO()
    
    #run through using cmdline topology option to make sure it doesn't
    #throw up an error
    sys.stdout = cmdResult
    inputArg = { 'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3,
    'nodes': ['a','b','c','d']}
    outputResult = None
    self.assertTrue(clockRelation.initClockRelation(cursor,inputArg)==outputResult)
    
    #run through using node topology from inputfile option to make sure it
    #doesn't throw up an error
    sys.stdout = fileResult
    inputArg = { 'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3,
    'nodes': []}
    self.assertTrue(clockRelation.initClockRelation(cursor,inputArg)==outputResult)
    
    #check to make sure that the outputs from both options are the same
    # where "options" := grabbing node topology from file OR 
    #                    grabbing node topology from the cmdline
    sys.stdout = originalStdout #return stdout to original 
    cmdOutput  = cmdResult.getvalue() [ cmdResult.getvalue().find('\n')  + 1 : ]
    fileOutput = fileResult.getvalue()[ fileResult.getvalue().find('\n') + 1 : ]
    self.assertEqual(cmdOutput,fileOutput)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )

  def test_buildClockRelation_clockRelation(self):
    #Not implemented in src yet
    return None

    
  # ///////////////////////////////////////////////// #
  #                  DEDALUS REWRITER                 #
  # ///////////////////////////////////////////////// #
  #TODO: clean up and add more specific testcases

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

    
  def test_getSubgoalsIDs_dedalusRewriter(self):
    return None   

  def test_getSubgoalAtts_dedalusRewriter(self):
    return None
    
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
    
  def test_rewriteDedalus_dedalusRewriter(self):
    return None


  # ///////////////////////////////////////////////// #
  #                PROVENANCE REWRITER                #
  # ///////////////////////////////////////////////// #

  def test_aggRuleProv_provenanceRewriter(self):
    return None 
    
  def test_getProv_provenanceRewriter(self):
    return None  
    
  def test_rewriteProvenance_provenanceRewriter(self):
    return None  


  # ///////////////////////////////////////////////// #
  #                       FACT                        #
  # ///////////////////////////////////////////////// #

  def test_getName_Fact( self ) :
    return None

  def test_getAttList_Fact( self ) :
    return None

  def test_getTimeArg_Fact( self ) :
    return None

  def test_setFactInfo_Fact( self ) :
    return None

  def test_setAttList_Fact( self ) :
    return None

  def test_setAttTypes_Fact( self ) :
    return None

  def test_getTypeList_Fact( self ) :
    return None

  def test_display_Fact( self ) :
    return None


  # ///////////////////////////////////////////////// #
  #                       RULE                        #
  # ///////////////////////////////////////////////// #

  def test_getGoalName_Rule( self ) :
    return None

  def test_getRewritten_Rule( self ) :
    return None

  def test_getGoalAttList_Rule( self ) :
    return None

  def test_getGoalTimeArg_Rule( self ) :
    return None

  def test_getSubgoalListStr_Rule( self ) :
    return None

  def test_getSubgoalListStr_noTimeArgs_noAddArgs_Rule( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
    return None

  def test_( self ) :
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
