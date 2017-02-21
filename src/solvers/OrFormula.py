#!/usr/bin/env python

'''
OrFormula.py
  definition of an OR boolean formula.
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys
from types import *

from BooleanFormula import BooleanFormula
import Literal

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


class OrFormula( BooleanFormula ) :

  ################
  #  ATTRIBUTES  #
  ################
  operator = None

  ################
  #  CONSTUCTOR  #
  ################
  def __init__( self ) :
    # BOOLEAN FORMULA CONSTRUCTOR left, right, value
    BooleanFormula.__init__(self, None, None, None)
    self.operator = "OR"

  ################
  #  IS LITERAL  #
  ################
  def isLiteral( self ) :
    return False


  #############
  #  ADD ARG  #
  #############
  def addArg( self, subfmla ) :

    newRight = OrFormula()
    newRight.left  = self.left
    newRight.right = self.right

    if newRight.left == None and newRight.right == None :
      self.isEmpty = True

    self.left  = subfmla
    self.right = newRight

    return self


#########
#  EOF  #
#########
