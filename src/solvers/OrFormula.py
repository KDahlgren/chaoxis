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

from BooleanFormula import BooleanFormula
import Literal

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


TESTING_MAIN = False


class OrFormula( BooleanFormula ) :

  ################
  #  ATTRIBUTES  #
  ################
  operator = None

  ################
  #  CONSTUCTOR  #
  ################
  def __init__( self ) :
    # BOOLEAN FORMULA CONSTRUCTOR left, right, val
    BooleanFormula.__init__(self, None, None, None)
    self.operator = "OR"


  #############
  #  ADD ARG  #
  #############
  def addArg( self, subfmla ) :
    
    # case formula is populated
    if self.fmla :
      #tools.bp( __name__, inspect.stack()[0][3], "BREAKHERE:\nself.fmla = " + str(self.fmla) + "\nsubfmla = " + str(subfmla) )

      # original fmla is the left argument to OR,
      # new subfmla is the right argument to OR
      self.left  = self.fmla
      self.right = subfmla
 
      # create the new fmla string
      self.fmla = "( " + str( self.fmla ) + " " + self.operator + " " + str( subfmla ) + " )"

    # no fmla currently exists
    # let fmla = subfmla and call the fmla the left argument of OR
    else :
      self.fmla = subfmla
      self.left = self.fmla

    return self.fmla


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



######################
#  MAIN FOR TESTING  #
######################
def main( ) :
  print "... TESTING ORFORMULA ..."
  a = Literal.Literal( "node(i,j,3)" )
  b = Literal.Literal( "node(j,k,3)" )
  print "a = " + str( a )
  print "b = " + str( b )

  f = OrFormula( a, b )
  print "f = " + str( f )


#########################
#  THREAD OF EXECUTION  #
#########################
if TESTING_MAIN :
  main()


#########
#  EOF  #
#########
