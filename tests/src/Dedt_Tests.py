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
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../../src" )
sys.path.append( packagePath )
testPath = os.path.abspath(__file__+"/../../../tests")



from dedt import dedt, Rule, Fact, dedalusParser, clockRelation, dedalusRewriter
from utils import dumpers, extractors, tools, parseCommandLineInput

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
    
    #checks if it runs through function without error
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
    
    #dependency
    dedc.createDedalusIRTables(cursor)
    
    #throws error for nonexistent file
    inputfile = "./nonexistentfile.ded"
    with self.assertRaises(SystemExit) as cm:
        dedc.dedToIR(inputfile,cursor)
    self.assertIn("ERROR",cm.exception.code)
    
    #runs through function to make sure it finishes without error
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
    #testing set up. runCompiler has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    
    #dependency
    dedc.createDedalusIRTables(cursor)
    
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    inputArg = {'prov_diagrams': False, 'use_symmetry': False, 'crashes': 0, 'solver': None, 
    'disable_dot_rendering': False, 'negative_support': False, 'strategy': None,
    'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3, 'find_all_counterexamples': False,
    'nodes': ['a', 'b', 'c', 'd'], 'EFF': 2}
    
    #runs through function to make sure it finishes without error
    outputResult = None
    self.assertFalse(dedc.runCompiler(cursor,inputfile,inputArg,None)==outputResult)
    c4file = dedc.runCompiler(cursor,inputfile,inputArg,None)
    
    
     #clean up testing
    IRDB.close()
    os.remove( testDB )
    if c4file is not None:
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
    #testing setup. initClockRelation has dependency
    #on createDedalusIRTables and dedToIR so that's
    #tested first above.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #Dependencies
    dedc.createDedalusIRTables(cursor)
    dedc.dedToIR( inputfile, cursor )
    
    #for saving the program clock output
    #to be used in comparison below
    clockRelation.CLOCKRELATION_DEBUG = True
    originalStdout= sys.stdout
    cmdResult = StringIO()
    fileResult = StringIO()
    
    #run through using cmdline topology option to make sure it doesn't
    #throw up an error
    sys.stdout = cmdResult
    inputArg = { 'file': testPath+"/testfiles/testFullProgram.ded", 'EOT': 3,
    'nodes': ['a','b','c','d']}
    outputResult = None
    self.assertTrue(clockRelation.initClockRelation(cursor,inputArg)==outputResult)
  
    #check to make sure that the outputs from both options are the same
    sys.stdout =originalStdout #return stdout to original 
    cmdOutput=cmdResult.getvalue()[cmdResult.getvalue().find('\n')+1:]
    fileOutput=fileResult.getvalue()[fileResult.getvalue().find('\n')+1:]
    self.assertEqual(cmdOutput,fileOutput)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )
  

  def test_buildClockRelation_clockRelation(self):
    return None
    
###########################
#  DEDALUSREWRITER TESTS  #
###########################

  #testing for the helper functions: getdeductiveRuleIDs,
  #getInductiveRuleIDs and getAsynchronousRuleIDs
  def test_getRuleIDs_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedc.createDedalusIRTables(cursor)
    dedc.dedToIR(inputfile,cursor)
    
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
     #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
   
    #dependency
    dedt.createDedalusIRTables(cursor)
    dedt.dedToIR(inputfile,cursor)
    iruleID = dedalusRewriter.getInductiveRuleIDs(cursor)
    druleID = dedalusRewriter.getDeductiveRuleIDs(cursor)
    aruleID = dedalusRewriter.getAsynchronousRuleIDs(cursor)
    
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getSubgoalIDs(cursor,iruleID[0])==None)
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getSubgoalIDs(cursor,druleID[0])==None)
    #runs through function to make sure it finishes without error
    self.assertFalse(dedalusRewriter.getSubgoalIDs(cursor,aruleID[0])==None)
    
    
    #clean up testing
    IRDB.close()
    os.remove( testDB )  

  def test_getSubgoalAtts_dedalusRewriter(self): 
    return None
    
  def test_rewriteDeductive_dedalusRewriter(self):
    #testing set up. Dependencies listed below.
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    inputfile = testPath+"/testfiles/testFullProgram.ded"
    
    #dependency
    dedc.createDedalusIRTables(cursor)
    dedc.dedToIR(inputfile,cursor)
    
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
    dedc.createDedalusIRTables(cursor)
    dedc.dedToIR(inputfile,cursor)
    
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
    dedc.createDedalusIRTables(cursor)
    dedc.dedToIR(inputfile,cursor)
    
    #runs through function to make sure it finishes without error
    self.assertTrue(dedalusRewriter.rewriteAsynchronous(cursor)==None)
    
    #clean up testing
    IRDB.close()
    os.remove( testDB ) 
    
  def test_rewriteDedalus_dedalusRewriter(self):
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


###################
#  RULE TESTS  #
###################


  #tests the creation of a new rule including the following helper functions
  # setGoalInfo(),setGoalAttList()
  # getGoalName(), getGoalAttList(), getGoalTimeArg()
  def test_getGoalName_Rule(self):
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    dedt.createDedalusIRTables(cursor)
    ruleTestA = ['node', '(', 'Node', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', 'Neighbor', ')']
    ruleTestB = ['log', '(', 'Node', 'Pload', ')', '@', 'next', ':-', 'log', '(', 'Node', 'Pload', ')']
    ruleTestC = ['post', '(', 'X', 'Pl', ')', ':-', 'log', '(', 'X', 'Pl', ')', ',', '___notin___missing_log', '(', '_', 'Pl', ')']
    ruleTest = [ruleTestA, ruleTestB, ruleTestC]
    
    for rule in ruleTest:
	#dependency
        rid = tools.getID()
	    # extract goal info
	goal          = extractors.extractGoal(rule)
	goalName      = extractors.extractName( goal )
	goalAttList   = extractors.extractAttList( goal)
	goalTimeArg   = extractors.extractTimeArg( goal)
	rewrittenFlag = 0 
	    
	newRule = Rule.Rule(rid, cursor  )
	    #testing
	self.assertTrue(newRule.setGoalInfo( goalName, goalTimeArg, rewrittenFlag )==None)
	self.assertTrue(newRule.setGoalAttList(goalAttList)==None)
	    
	self.assertTrue(goalName==str(newRule.getGoalName()))
	self.assertTrue(str(goalAttList)==str(newRule.getGoalAttList()))
	self.assertTrue(str(goalTimeArg)==str(newRule.getGoalTimeArg()))
     
   #clean up testing
    IRDB.close()
    os.remove( testDB )   
   
  def test_getSubgoalListStr_Rule(self):
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    dedt.createDedalusIRTables(cursor)
    ruleTestA = ['node', '(', 'Node', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', 'Neighbor', ')']
    ruleTestB = ['log', '(', 'Node', 'Pload', ')', '@', 'next', ':-', 'log', '(', 'Node', 'Pload', ')']
    ruleTest = [ruleTestA, ruleTestB]
    
    for rule in ruleTest:
    	#dependency
        subgoalList = extractors.extractSubgoalList( rule )
        for sub in subgoalList:
		sid = tools.getID()
		rid = tools.getID()
		subgoalName    = extractors.extractSubgoalName( sub )
		subgoalAttList = extractors.extractAttList( sub ) # returns list
		subgoalTimeArg = extractors.extractTimeArg(  sub )
		subgoalAddArgs = extractors.extractAdditionalArgs( sub ) # returns list
		newRule = Rule.Rule(rid, cursor  )
		
		#testing
		self.assertTrue(newRule.setSingleSubgoalInfo( sid, subgoalName, subgoalTimeArg )==None)
		self.assertTrue(newRule.setSingleSubgoalAttList( sid, subgoalAttList )==None)
		self.assertTrue(newRule.setSingleSubgoalAddArgs( sid, subgoalAddArgs )==None)

	        testCheck = subgoalName+'('
	        for att in subgoalAttList[:-1]:
	            testCheck +=att+','
	        else:
	            testCheck +=subgoalAttList[-1]+')'
	        
                self.assertTrue(testCheck==newRule.getSubgoalListStr())

    #clean up testing
    IRDB.close()
    os.remove( testDB ) 
    
  def test_getEquationListStr_Rule(self):
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB ) 
    cursor  = IRDB.cursor()
    dedt.createDedalusIRTables(cursor)
    ruleTestA = ['node', '(', 'Node', 'Neighbor', ')', '@', 'next', ':-', 'node', '(', 'Node', 'Neighbor', ')']
    ruleTestB = ['log', '(', 'Node', 'Pload', ')', '@', 'next', ':-', 'log', '(', 'Node', 'Pload', ')']
    ruleTestC = ['post', '(', 'X', 'Pl', ')', ':-', 'log', '(', 'X', 'Pl', ')', ',', '___notin___missing_log', '(', '_', 'Pl', ')']
    ruleTest = [ruleTestA, ruleTestB, ruleTestC]
    
    eqnList = extractors.extractEqnList( ruleTestA )

    for eqn in eqnList :
        # generate random ID for eqn
        eid = tools.getID()

        print eqn
    #clean up testing
    IRDB.close()
    os.remove( testDB ) 
    
###################
#  FACT TESTS  #
###################
   #test fact creation and functions
  def test_Fact_Fact(self):
       testDB = testPath + "/IR.db"
       IRDB    = sqlite3.connect( testDB ) 
       cursor  = IRDB.cursor()
       dedt.createDedalusIRTables(cursor)
       factTestA =  ['node', '(', '"a","b"', ')', '@', '1']
       factTestB = ['node', '(', '"a","c"', ')', '@', '1']
       factTestC = ['bcast', '(', '"a","hello"', ')', '@', '1']
       factTest = [factTestA, factTestB, factTestC]
       for fact in factTest:
       	   # dependency
           fid = tools.getID()
           # extract fact info
           name    = extractors.extractName( fact)
           attList = extractors.extractAttList( fact )
           attList = attList[0].split( "," )
           timeArg = extractors.extractTimeArg( fact )
           
           newFact = Fact.Fact( fid, cursor )
           self.assertTrue(newFact.setFactInfo( name, timeArg )==None)
           self.assertTrue(newFact.setAttList(  attList )==None)
           self.assertTrue( name==str( newFact.getName() ))
           self.assertTrue(str(attList)== str( newFact.getAttList() ))
           self.assertTrue(str(timeArg == str( newFact.getTimeArg() )))

      #clean up testing
       IRDB.close()
       os.remove( testDB )
#########################
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
    unittest.main( verbosity=2 )


#########
#  EOF  #
#########
