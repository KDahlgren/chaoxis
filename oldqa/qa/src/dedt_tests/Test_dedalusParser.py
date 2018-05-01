#!/usr/bin/env python

'''
Test_dedalusParser.py
  Defines unit tests for dedalusParser.py in src/dedt/.
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
#  TEST DEDALUS PARSER  #
#########################
class Test_dedalusParser( unittest.TestCase ) :


  ##################
  #  CLEAN RESULT  #
  ##################
  def test_cleanResult_dedalusParser(self):
    inputArg  = ('node', '(', 'Node', ',', ' ', 'Neighbor', ')', ';')
    outputResult = ['node', '(', 'Node', ',', ' ', 'Neighbor', ')', ';']
    self.assertEqual(dedalusParser.cleanResult(inputArg),outputResult)


  ###########
  #  PARSE  #
  ###########
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


  ###################
  #  PARSE DEDALUS  #
  ###################
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
#  THREAD OF EXECUTION  #
#########################
# use this main if running this script exclusively.
if __name__ == "__main__" :
    unittest.main( verbosity=2 )


#########
#  EOF  #
#########
