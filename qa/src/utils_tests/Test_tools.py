#!/usr/bin/env python

'''
Test_tools
  Defines unit tests for tools.py from utils/.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )

from utils import tools, extractors, parseCommandLineInput

# ------------------------------------------------------ #

testPath = os.path.abspath(__file__+"/../../../../qa")

################
#  TEST TOOLS  #
################
class Test_tools( unittest.TestCase ) :


  ################
  #  BREAKPOINT  #
  ################
  def test_bp_tools( self ) :
    with self.assertRaises(SystemExit) as cm:
      tools.bp("testfile", "testfunc", "testmsg")
    self.assertTrue(cm.exception.code in "BREAKPOINT in file testfile at function testfunc :\n>>> testmsg FAIL")


  ############
  #  GET ID  #
  ############
  def test_getID_tools( self ) :
    outputResult = 16
    self.assertEqual( len( tools.getID( ) ), outputResult )
    self.assertTrue(tools.getID( ).isalpha())
    self.assertTrue(tools.getID( ).islower())


  #########################
  #  GET RANDOM ATT NAME  #
  #########################
  def test_getRandomAttName( self ) :
    outputResult = 16
    self.assertEqual( len( tools.getRandomAttName( ) ), outputResult )
    self.assertTrue(tools.getRandomAttName( ).isalpha())
    self.assertTrue(tools.getRandomAttName( ).isupper())


  #########################
  #  GET EVAL RESULTS C4  #
  #########################
  def test_getEvalResultsC4_tools( self ) :
    c4respath = testPath  + "/testfiles/c4dump.txt"
    with self.assertRaises(SystemExit) as cm:
      tools.getEvalResults_file_c4("")
    self.assertTrue(cm.exception.code=="Cannot open file : ")
    dictRes = tools.getEvalResults_file_c4(c4respath)
    self.assertFalse(dictRes['node']==None)
    self.assertFalse(dictRes['pre']==None)
    self.assertFalse(dictRes['post']==None)


  ################################
  #  CHECK IF REWRITTEN ALREADY  #
  ################################
  def test_checkIfRewrittenAlready_tools( self ) :
    return None


  #######################
  #  CHECK PARENTHESES  #
  #######################
  def test_checkParentheses_tools( self ) :
    inputArg  = "node(Node, Neighbor)@next :- node(Node, Neighbor) ;"
    outputResult = True
    self.assertEqual( tools.checkParentheses( inputArg ), outputResult )


  ###################
  #  TO ASCII LIST  #
  ###################
  def test_toAscii_list_tools( self ) :
    unitestfile = testPath + "/testfiles/unicodetest.txt"
    with open(unitestfile,"r") as f:
      line = f.readlines()[0][6:]
      x = 0
      testmulti = []
      while x != 5:
        testmulti.append(line)
        x= x+1
      self.assertFalse(tools.toAscii_list(testmulti)==None)


  #########################
  #  TO ASCII MULTI LIST  #
  #########################
  def test_toAscii_multiList_tools( self ) :
    unitestfile = testPath + "/testfiles/unicodetest.txt"
    with open(unitestfile,"r") as f:
      line = [f.readlines()[0][6:]]
      x = 0
      testmulti = []
      while x != 5:
        testmulti.append(line)
        x= x+1
      self.assertFalse(tools.toAscii_multiList(testmulti)==None)


  ##################
  #  TO ASCII STR  #
  ##################
  def test_toAscii_str_tools( self ) :
    unitestfile = testPath + "/testfiles/unicodetest.txt"
    with open(unitestfile,"r") as f:
      line = [f.readlines()[0][6:]]
      line = tools.toAscii_str(line)
      self.assertFalse(line.decode('utf-8')==None)


  ##########
  #  SKIP  #
  ##########
  def test_skip_tools( self ) :
    testline = "\n"
    self.assertTrue(tools.skip(testline)==True)
    testline = "/       "
    self.assertTrue(tools.skip(testline)==True)
    testline = "hello world / !"
    self.assertTrue(tools.skip(testline)==False)


  ############################
  #  GET ALL INCLUDED FILES  #
  ############################
  def test_getAllIncludedFiles_tools( self ) :
    #Test: base case
    testDict = {"Utils_Tests.py": True}
    self.assertTrue(tools.getAllIncludedFiles(testDict)==testDict)
    #Test: Unable to find file error hit
    testDict = {"FakeFile": False}
    with self.assertRaises(SystemExit) as cm:
      tools.getAllIncludedFiles(testDict)
    self.assertTrue("ERROR" in cm.exception.code)
    #Test: Succesfully finding included files in .ded
    dedtestfile = testPath + "/testfiles/testInclude.ded"
    testDict = {dedtestfile: False}
    self.assertTrue(tools.getAllIncludedFiles(testDict)==testDict)


  ###################
  #  COMBINE LINES  #
  ###################
  def test_combineLines_tools( self ) :
    testList = [["Hello"],["World","!"],["!"]]
    self.assertTrue(tools.combineLines(testList)=="HelloWorld!!")


  ######################
  #  ATT SEARCH PASS 2 #
  ######################
  def test_attSearchPass2_tools( self ) :
    testList = "datalog,Rule,THISISAWILDCARDNFDEICZANGTPSRFE,Hello,\
    THISISAWILDCARDCATDOGANEUXLFEVN,World"
    outputList = ["THISISAWILDCARDNFDEICZANGTPSRFE",
    "THISISAWILDCARDCATDOGANEUXLFEVN"]
    self.assertTrue(len(tools.attSearchPass2(testList))==2)
    self.assertTrue(tools.attSearchPass2(testList)==outputList)


  #############
  #  IS FACT  #
  #############
  def test_isFact_tools( self ) :
    return None


  ######################
  #  CHECK DATA TYPES  #
  ######################
  def test_checkDataTypes_tools( self ) :
    return None


  ###############
  #  IS STRING  #
  ###############
  def test_isString_tools( self ) :
    testVar = "'String'"
    self.assertTrue(tools.isString(testVar)==True)
    testVar = '"String"'
    self.assertTrue(tools.isString(testVar)==True)
    testVar = '9'
    self.assertTrue(tools.isString(testVar)==False)


  ############
  #  IS INT  #
  ############
  def test_isInt_tools( self ) :
    testVar = "!!!!"
    self.assertTrue(tools.isInt(testVar)==False)
    testVar = '"String"'
    self.assertTrue(tools.isInt(testVar)==False)
    testVar = '123456789'
    self.assertTrue(tools.isInt(testVar)==True)


  ##################
  #  GET VAR TYPE  #
  ##################
  def test_getVarType_tools( self ) :
    return None


  ##################
  #  CONTAINS EQN  #
  ##################
  def test_containsEqn_tools( self ) :
    return None


#########
#  EOF  #
#########
