#!/usr/bin/env python

'''
CNFFormula.py
  definition of the CNF formula structure
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

DEBUG = True


class CNFFormula( ) :

  ################
  #  ATTRIBUTES  #
  ################
  formula = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, formula ) :

    form = formula

    # transform given formula into CNF
    while not form == self.formula :

      if DEBUG :
        print str(form) + " IS NOT == " + str(self.formula)

      self.formula = form
      form = form.toCNF()

    self.formula = form.convertToCNF()


  ###############
  #  CONJUNCTS  #
  ###############
  # return the conjunctive clauses of this formula
  def conjuncts( self ) :
    return self.formula.conjuncts() 


#########
#  EOF  #
#########
