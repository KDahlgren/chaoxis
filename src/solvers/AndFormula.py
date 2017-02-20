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
# standard python packages
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

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, left, right ) :
    # BOOLEAN FORMULA CONSTRUCTOR left=None, right=None, val=None
    BooleanFormula.__init__(self, left, right)
    self.operator = "AND"


  ############
  #  TO CNF  #
  ############
  # implementing abstract BooleanFormula method.
  # converts formula into CNF form
  def toCNF( self ) :
    return AndFormula( self.left.toCNF(), self.right.toCNF() )  


  ############
  #  IS CNF  #
  ############
  # implementing abstract BooleanFormula method.
  # checks if formula is in CNF
  def isCNF( self ) :
    return self.left.isCNF() and self.right.isCNF()


  ###############
  #  DISJUNCTS  #
  ###############
  # ????
  # return an empty set
  def disjuncts( self ) :
    return set()


  ###############
  #  CONJUNCTS  #
  ###############
  # implementing abstract BooleanFormula method.
  # return list of conjuncted sub-formulas of this boolean formula.
  def conjuncts(self):
    # an AND node should return a set of sets of disjuncts
    #return self.left.conjuncts().union(self.right.conjuncts())

    ret = set() # sets protect against duplicate sub-formulas =]

    # --------------------------------------------------- #
    #  examine left argument

    # case left argument is an OR formula
    if self.left.operator == "OR" :
      ret.add( frozenset( self.left.disjuncts() ) )

    # case left is an AND formula or a literal
    else:
      ret = ret.union(self.left.conjuncts())

    # --------------------------------------------------- #
    #  examine right argument

    # case right is an OR formula
    if self.right.operator == "OR" :
      ret.add( frozenset( self.right.disjuncts() ) )

    # case right is an AND formula or a literal
    else:
      ret = ret.union( self.right.conjuncts() )

    # --------------------------------------------------- #

    return ret


#########
#  EOF  #
#########
