#!/usr/bin/env python

'''
AndFormula.py
  definition of an AND boolean formula.
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
import inspect, os, sys

from BooleanFormula import BooleanFormula

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #



class AndFormula( BooleanFormula ) :

  ################
  #  ATTRIBUTES  #
  ################
  operator = None
  unary    = None

  #################
  #  CONSTRUCTOR  #
  #################
  # listOfProvDescendants is either 
  #  1. a list of goal-rooted trees or 
  #  2. a single fact-rooted tree
  def __init__( self ) :

    # BOOLEAN FORMULA CONSTRUCTOR left, right, value
    BooleanFormula.__init__( self, None, None, None )
    self.operator = "AND"


#########
#  EOF  #
#########
