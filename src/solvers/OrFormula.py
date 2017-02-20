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

import BooleanFormula

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
  def __init__( self, left, right ) :
    # BOOLEAN FORMULA CONSTRUCTOR left=None, right=None, val=None
    BooleanFormula.__init__(self, left, right)
    self.operator = "OR"


  ############
  #  TO CNF  #
  ############
  # convert this boolean formula to CNF
  def toCNF( self ) :

    # case right is an AND formula
    if self.right.sign == "AND":
      lft = self.left.toCNF()
      return AndFormula( OrFormula( lft, self.right.left.toCNF()), OrFormula( lft, self.right.right.toCNF() ) )

    # case left is an AND formula
    elif self.left.sign == "AND":
      rgh = self.right.toCNF()
      return AndFormula( OrFormula( self.left.left.toCNF(), rgh ), OrFormula( self.left.right.toCNF(), rgh ) )

    # case both right and left are OR formulas
    else:
      return OrFormula( self.left.toCNF(), self.right.toCNF() )


  ############
  #  IS CNF  #
  ############
  # //
  def isCNF( self ) :

    # case either left or right argument is an AND formula
    if (self.left.operator == "AND") or (self.right.operator == "AND"):
      print "Formula is not in CNF : " + self.left.operator + " and " + self.right.operator
      return False

    # both left and right are OR formulas
    # recursively examine left and right formulas for isCNF
    else:
      return self.left.isCNF() and self.right.isCNF()


  ###############
  #  DISJUNCTS  #
  ###############
  # return the set of disjunctive clauses
  def disjuncts( self ) :

    # case formula is not in CNF
    if not self.isCNF() :
      raise Exception("Formula not CNF")

    # case formula is in CNF
    else:
      return self.left.disjuncts().union(self.right.disjuncts())


