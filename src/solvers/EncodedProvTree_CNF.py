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


DEBUG = False


class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  rawformula = None  # a BooleanFormula, not neccessarily in CNF
  cnfformula = None  # a CNF formula string


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ) :
    self.rawformula         = solverTools.convertToBoolean( provTree )
    self.rawBooleanFmla_str = self.rawformula.display()
    self.cnfformula         = solverTools.convertToCNF( self.rawBooleanFmla_str )

  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return self.cnfformula


#########
#  EOF  #
#########
