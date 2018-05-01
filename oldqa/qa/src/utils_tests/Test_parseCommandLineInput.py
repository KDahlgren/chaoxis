#!/usr/bin/env python

'''
Test_parseCommandLineInput.py
  Defines unit tests for parseCommandLineInput.py from utils/.
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

##################################
#  TEST PARSE COMMANDLINE INPUT  #
##################################
class Test_parseCommandLineInput( unittest.TestCase ) :


  ##############################
  #  PARSE COMMAND LINE INPUT  #
  ##############################
  def parseCommandLineInput( self ) :
    return None


#########
#  EOF  #
#########
