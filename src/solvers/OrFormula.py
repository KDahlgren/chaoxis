#!/usr/bin/env python

'''
OrFormula.py
  definition of an OR boolean formula.
  borrows elements from https://github.com/palvaro/ldfi-py
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
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utilities import tools

# **************************************** #


class OrFormula( BooleanFormula ) :

  ################
  #  ATTRIBUTES  #
  ################
  operator = None
  unary    = None

  ################
  #  CONSTUCTOR  #
  ################
  def __init__( self ) :

    # BOOLEAN FORMULA CONSTRUCTOR left, right, value
    BooleanFormula.__init__( self, None, None, None )
    self.operator = "OR"


#########
#  EOF  #
#########
