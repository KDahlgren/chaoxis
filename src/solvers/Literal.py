#!/usr/bin/env python

'''
Literal.py
  definition of boolean formula consisting only of a single literal
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

from BooleanFormula import BooleanFormula

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


class Literal( BooleanFormula ) :

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, value ) :
    # BOOLEAN FORMULA CONSTRUCTOR left, right, value
    BooleanFormula.__init__( self, None, None, value )

  ################
  #  IS LITERAL  #
  ################
  def isLiteral( self ) :
    return True


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return self.value


#########
#  EOF  #
#########
