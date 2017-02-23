#!/usr/bin/env python

'''
EncodedProvTree.py
  code for encoding a given provenance tree
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

import AndFormula, OrFormula, Literal, solverTools

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


DEBUG = True


class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  formula  = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ):
    self.formula  = solverTools.convertToCNF( provTree ) # returns a BooleanFormula


#########
#  EOF  #
#########
