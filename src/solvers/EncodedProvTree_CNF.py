#!/usr/bin/env python

'''
EncodedProvTree.py
  code for encoing a given provenance tree
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

import AndFormula, OrFormula, Literal

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  provTree = None
  formula  = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ):
    self.provTree = provTree
    self.CNFFormula  = self.convertToCNF( self.provTree )


  ####################
  #  CONVERT TO CNF  #
  ####################
  # recursively construct a CNF formula from the given prov tree
  def convertToCNF( self, provTree ) :

    # handle ultimate goal
    if provTree.isUltimateGoal( ) :
      return None

    # base case: provTree is a fact
    elif provTree.root.treeType == "fact" :
      #return Literal(  )
      return None

    # case root is a goal
    elif provTree.root.treeType == "goal" :
      return None
      #long = self.formula(depth-1)
      #short = self.formula(random.randint(1, depth-1))

      #if random.randint(0,1) == 1:
      #  left = long
      #  right = short

      #else:
      #  right = long
      #  left = short

      ## either an AND or an OR
      #if random.randint(0,1) == 1:
      #  # AND
      #  return AndFormula(left, right)
      #else:
      #  OrFormula(left, right)

    # case root is a rule
    elif provTree.root.treeType == "rule" :
      return None

    # case root is not an ultimate goal, fact, goal, or rule
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: Attempting to generate CNF formula from provenance tree. Hit a node which is not an UltimateGoal, fact, goal, or rule:\n" + str(provTree.root) + " is of type " + str(provTree.root.treeType) )


#########
#  EOF  #
#########
