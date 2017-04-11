#!/usr/bin/env python

'''
VizTools_Tests.py
  Defines unit tests for vizTools.
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

from visualizations import *
# ------------------------------------------------------ #


####################
#  VIZTOOLS TESTS  #
####################
class VizTools_Tests( unittest.TestCase ) :

  def test__vizTools( self ) :
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
