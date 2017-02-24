#!/usr/bin/env python

'''
EncodedProvTree.py
  code for encoding a given provenance tree
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys
from types import *

import AndFormula, OrFormula, Literal
import psat

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


DEBUG = True


###############
#  SOLVE CNF  #
###############
def solveCNF( cnfFormula ) :

  print "cnfFormula.getConjuncts() = " + str( cnfFormula.getConjuncts() )

  # get solutions
  solns = psat.Solver( cnfFormula )

  #if DEBUG :
  #  for soln in  solns.minimal_solutions():
  #    print "SOLN " + str(soln)

  return solns


#####################
#  CONVERT TO CNF  #
#####################
def convertToCNF( provTree ) :

  if not provTree.isUltimateGoal() :
    displayTree( provTree )

  fmla = None # initialize

  # -------------------------------------------------- #
  # case prov tree rooted at an ultimate goal
  #
  # always only one right goal => builds forumlas up from the left with parens:
  #    ( ( ... ) OP fmla_m-1 ) OP fmla_m
  #
  if provTree.isUltimateGoal() :
    fmla      = AndFormula.AndFormula() # empty
    leftGoals = provTree.subtrees[:-1]  # of type list
    rightGoal = provTree.subtrees[-1]   # not a list

    # branch on left rules contents
    if len( leftGoals ) > 1 :
      fmla.left = getLeftFmla( leftGoals, "AND" )
      fmla.right  = convertToCNF( rightGoal )

    elif len( leftGoals ) < 1 :
      fmla.unary = convertToCNF( rightGoal )

    else : # leftGoals contains only one goal
      fmla.left  = convertToCNF( leftGoals[0] )
      fmla.right = convertToCNF( rightGoal )

    # sanity check
    if fmla.left and fmla.unary :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR1: self.left and self.unary populated for the same formula!")

  # -------------------------------------------------- #
  # case prov tree rooted at goal
  elif provTree.root.treeType == "goal" :

    # case goal is negative => change when supporting negative provenance.
    if len( provTree.root.descendants ) == 0 :
      #fmla       = OrFormula.OrFormula()
      print " > Adding " + str( provTree.root ) + " to fmla unary."
      #fmla.unary = Literal.Literal( str( provTree.root ) )
      fmla       = Literal.Literal( str( provTree.root ) )

    # case goal has 1 or more rule descendants only
    elif checkDescendantTypes( provTree, "rule" ) :
      fmla      = OrFormula.OrFormula()          # empty
      leftRules = provTree.root.descendants[:-1] # of type list
      rightRule = provTree.root.descendants[-1]  # not a list

      # branch on left rules contents
      if len( leftRules ) > 1 :
        fmla.left   = getLeftFmla( leftRules, "AND" )
        fmla.right  = convertToCNF( rightRule )
        fmla.unary  = None

      elif len( leftRules ) < 1 :
        fmla.left  = None
        fmla.unary = convertToCNF( rightRule )
        #fmla.unary = "shit"

      else : # leftRules contains only one rule
        fmla.unary = None
        fmla.left  = convertToCNF( leftRules[0] )
        fmla.right = convertToCNF( rightRule )

    # case goal has one or more fact descendants only
    # goals with more than 1 fact contain wildcards
    #   Simplify representation by presenting the wilcard version
    #   because the wildcard fact is true if any of the underlying
    #   facts are true.
    elif checkDescendantTypes( provTree, "fact" ) :
      print " > Adding " + str( provTree.root ) + " to fmla."
      fmla = Literal.Literal( str( provTree.root ) ) # <--- BASE CASE!!!
      print " > Added " + str( provTree.root ) + " to fmla."

    # case universe implodes
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: goal unrecognized goal descendant pattern: provTree.root.descendants : " + str( provTree.root.descendants ) )

    # sanity check
    if fmla.left and fmla.unary :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR2: self.left and self.unary populated for the same formula!")

  # -------------------------------------------------- #
  # case prov tree rooted at rule
  elif provTree.root.treeType == "rule" :
    fmla      = AndFormula.AndFormula()        # empty
    leftGoals = provTree.root.descendants[:-1] # of type list
    rightGoal = provTree.root.descendants[-1]  # not a list

    # branch on left goals contents
    if len( leftGoals ) > 1 :
      #fmla.left  = getLeftFmla( leftGoals, "OR" )
      fmla.left  = getLeftFmla( leftGoals, "AND" )
      fmla.right = convertToCNF( rightGoal )

    elif len( leftGoals ) < 1 :
      fmla.unary = convertToCNF( rightGoal )

    else : # leftGoals contains only one goal
      fmla.left  = convertToCNF( leftGoals[0] )
      fmla.right = convertToCNF( rightGoal )

    # sanity check
    if fmla.left and fmla.unary :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR3: self.left and self.unary populated for the same formula!")

  # -------------------------------------------------- #
  # case universe explodes
  else :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: prov tree root is not an ultimate goal, a goal, or a rule: provTree.root.treeType = " + str( provTree.root.treeType ) )

  # sanity check
  if fmla.left and fmla.unary :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR4: self.left and self.unary populated for the same formula!")

  return fmla


###########
#  MERGE  #
###########
def merge( subfmlas, op ) :

  fmla = None # initialize

  # branch on operator
  if op == "AND" :
    fmla = AndFormula.AndFormula() # empty
  elif op == "OR" :
    fmla = OrFormula.OrFormula()   # empty
  else :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: unrecognized operator : " + str( op ) )

  # sanity check
  if fmla :

    # case multiple subformulas exist
    if len( subfmlas ) > 1 :
        fmla.left  = merge( subfmlas[:-1], op ) # subfmlas[:-1] is of type list
        fmla.right = merge( [ subfmlas[-1] ], op ) # subfmlas[-1] is of type BooleanFormula

    # case no subformulas exist
    elif len( subfmlas ) < 1 :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: subfmlas is empty." )

    # case only one subformula exists
    else :
      fmla.unary = subfmlas[0]

  else :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: fmla does not exist." )

  return fmla


###################
#  GET LEFT FMLA  #
###################
def getLeftFmla( provTreeList, op ) :

  mergeFmla = None
  subfmlas = []

  for provTree in provTreeList :
    #displayTree( provTree )
    subfmlas.append( convertToCNF( provTree ) )

  mergedFmla = merge( subfmlas, op )

  return mergedFmla


##################
#  DISPLAY TREE  #
##################
# input provenance tree
# display relevant info about the tree to stdout
# good for debugging
def displayTree( tree ) :
  print
  print "----------------------------------------------------"
  print "  tree.root.name     = " + str( tree.root.name ) 
  print "  tree.root.treeType = " + str( tree.root.treeType )
  print "  tree.root.record   = " + str( tree.root.record )
  print "  tree.root.isNeg    = " + str( tree.root.isNeg ) 
  print "  len( tree.root.descendants ) = " + str( len( tree.root.descendants ) )
  for desc in tree.root.descendants :
    print "     desc.root.name               = " + str( desc.root.name ) 
    print "     desc.root.treeType           = " + str( desc.root.treeType )
    print "     desc.root.record             = " + str( desc.root.record )
    print "     desc.root.isNeg              = " + str( desc.root.isNeg ) 
    if not desc.root.treeType == "fact" :
      print "     len( desc.root.descendants ) = " + str( len( desc.root.descendants ) )
    else :
      print "     len( desc.root.descendants ) = 0"


############################
#  CHECK DESCENDANT TYPES  #
############################
def checkDescendantTypes( provTree, targetType ) :

  descList = provTree.root.descendants

  for d in descList :
    if not d.treeType == targetType :
      return False

  return True



#########
#  EOF  #
#########
