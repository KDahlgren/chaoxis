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


TESTING_MAIN = False


class Literal( BooleanFormula ) :

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, val ) :
    # BOOLEAN FORMULA CONSTRUCTOR left, right, val
    BooleanFormula.__init__(self, None, None, val)
    self.fmla = val


  ############
  #  TO CNF  #
  ############
  # literals satisfy the definition of CNF formula by default.
  def toCNF( self ) :
    return self


  ############
  #  IS CNF  #
  ############
  # ditto: literals satisfy the definition of CNF formula by default.
  def isCNF( self ) :
    return True


  ###############
  #  DISJUNCTS  #
  ###############
  # represent the literal as a disjunctive formula
  def disjuncts( self ) :
    return set( [ self.val ] )


######################
#  MAIN FOR TESTING  #
######################
def main( ) :
  print "... TESTING LITERAL ..."
  a = Literal( "node(1,2,3)" )
  print "a = " + str( a )

#########################
#  THREAD OF EXECUTION  #
#########################
if TESTING_MAIN :
  main()

#########
#  EOF  #
#########
