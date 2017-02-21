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
import Literal

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


TESTING_MAIN = False


class AndFormula( BooleanFormula ) :

  ################
  #  ATTRIBUTES  #
  ################
  operator = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self ) :
    # BOOLEAN FORMULA CONSTRUCTOR left, right, val
    BooleanFormula.__init__( self, None, None, None)
    self.operator = "AND"


  #############
  #  ADD ARG  #
  #############
  def addArg( self, subfmla ) :

    # case formula is populated
    if self.fmla :

      # original fmla is the left argument to AND,
      # new subfmla is the right argument to AND
      self.left  = self.fmla
      self.right = subfmla

      # create the new fmla string
      self.fmla = "( " + str( self.fmla ) + " " + self.operator + " " + str( subfmla ) + " )"

    # no fmla currently exists
    # let fmla = subfmla and call the fmla the left argument of AND.
    else :
      self.fmla = subfmla
      self.left = self.fmla

    return self.fmla


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
  # clauses in AND formulas are conjuncts, not disjuncts
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


######################
#  MAIN FOR TESTING  #
######################
def main( ) :
  print "... TESTING ANDFORMULA ..."
  a = Literal.Literal( "node(i,j,3)" )
  b = Literal.Literal( "node(j,k,3)" )
  print "a = " + str( a )
  print "b = " + str( b )

  f = AndFormula( a, b )
  print "f = " + str( f )


#########################
#  THREAD OF EXECUTION  #
#########################
if TESTING_MAIN :
  main()


#########
#  EOF  #
#########
