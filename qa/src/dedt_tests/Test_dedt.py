#!/usr/bin/env python

'''
Test_Dedt.py
  Defines unit tests for dedt.py from src/dedt/
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


###############
#  TEST DEDT  #
###############
class Test_dedt( unittest.TestCase ) :


  ##############################
  #  CREATE DEDALUS IR TABLES  #
  ##############################
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
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SubgoalAtt'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SubgoalAddArgs'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Equation'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Clock'").fetchone()==None)
    self.assertFalse(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Crash'").fetchone()==None)
  
    #clean up testing
    IRDB.close()
    os.remove( testDB )
    

  ################
  #  DEDT TO IR  #
  ################
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


  ###################
  #  STARTER CLOCK  #
  ###################
  def test_starterClock_dedt( self ) :
    #tested in clockRelation tests below
    return None


  ############
  #  REWRITE #    
  ############
  def test_rewrite_dedt( self ) :
    #tested in dedalusRewriter and
    #provenanceRewriter below
    return None


  ####################
  #  RUN TRANSLATOR  #
  ####################
  def test_runTranslator_dedt( self ) :
    #testing set up. runTranslator has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB      = testPath + "/IR.db"
    IRDB        = sqlite3.connect( testDB ) 
    cursor      = IRDB.cursor()

    tableList   = testPath  + "/testfiles/tableListStr.data"
    datalogProg = testPath  + "/testfiles/c4program.olg"

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


    with self.assertRaises( SystemExit ) :
      dedt.runTranslator(cursor,inputfile,inputArg,tableList,None,evaluator)

    outpaths     = dedt.runTranslator(cursor,inputfile,inputArg,tableList,datalogProg,evaluator)

    if not outpaths is None :
      tables       = outpaths[0]
      c4file       = outpaths[1]

      #clean up testing
      IRDB.close()
      os.remove( testDB )
      if tables is not None:
        os.remove(tables)
      if c4file is not None:
        os.remove(c4file)


  #######################
  #  TRANSLATE DEDALUS  #
  #######################
  def test_translateDedalus_dedt( self ) :
 
    testDB = testPath + "/IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()
 
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
    tableList   = testPath  + "/testfiles/tableListStr.data"
    datalogProg = testPath  + "/testfiles/c4program.olg"
    outputResult = None
    self.assertTrue(dedt.translateDedalus(inputArg, tableList, datalogProg, cursor)==outputResult)


  ##############
  #  CLEAN UP  #
  ##############
  def test_cleanUp( self ) :
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
