#!/usr/bin/env python

'''
Visualizations_Tests.py
  Defines unit tests for visualizations.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../src" ) )

from visualizations import *
# ------------------------------------------------------ #


##########################
#  VISUALIZATIONS TESTS  #
##########################
class Visualizations_Tests( unittest.TestCase ) :

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
