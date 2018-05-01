#!/usr/bin/env python

'''
Test_clockRelation.py
  Defines unit tests for clockRelation.py in src/dedt/.
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


#########################
#  TEST CLOCK RELATION  #
#########################
class Test_clockRelation( unittest.TestCase ) :

  #########################
  #  INIT CLOCK RELATION  #
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


  ##########################
  #  BUILD CLOCK RELATION  #
  ##########################
  def test_buildClockRelation_clockRelation(self):
    #Not implemented in src yet
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
