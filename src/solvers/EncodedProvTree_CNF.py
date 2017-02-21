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

import AndFormula, OrFormula, Literal

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


DEBUG = True


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
    self.formula  = self.convertToCNF( self.provTree ) # a BooleanFormula


  ####################
  #  CONVERT TO CNF  #
  ####################
  # recursively construct a CNF formula from the given prov tree
  def convertToCNF( self, provTree ) :

    currFmla = None  # initialize current formula

    # ------------------------------------------- #
    #        BASE CASE : provTree is a fact       #
    # ------------------------------------------- #
    if provTree.isLeaf() :

      if provTree.treeType == "fact" :
        print "--------"
        print "fact: provTree.root.name ~> " + str( provTree.root.name ) + str( provTree.root.record ) + ", type = " + str(provTree.root.treeType)

        print "> Creating Literal for fact " + str( provTree.root.name ) + str( provTree.root.record )
        currFmla = Literal.Literal( provTree.root.fmlaDisplay() )

    else :
      # ------------------------------------------- #
      # case prov tree is rooted at an ultimate goal
      # then the CNF interpretation requires AND'ing all subgoals
      if provTree.isUltimateGoal() :

        print "--------"
        print " ULTIMATE GOAL : " + str( provTree.rootname ) + " has " + str( len(provTree.subtrees) ) + " descendants :"
        for d in provTree.subtrees :
          print "ult.goal desc : d.root ~> " + str(d.root.name) + str(d.root.record) + ", type = " + str(d.root.treeType)

        print "> Creating AndFormula for UG " + str( provTree.rootname )
        currFmla = AndFormula.AndFormula()  # start with an empty AND formula
        # add CNF formulas of subtrees as args in this AND formula
        for subtree in provTree.subtrees :
          print "  Examining " + str(subtree.root.treeType) + " " + str( subtree.root.name ) + str( subtree.root.record )
          currFmla.addArg( self.convertToCNF( subtree ) )

      # ------------------------------------------- #
      # case root is a goal
      # then the CNF interpretation requires OR'ing all contributing rules
      elif provTree.root.treeType == "goal" :

        print "--------"
        print " GOAL : " + str( provTree.root.name ) + str( provTree.root.record ) + " has " + str( len(provTree.root.descendants) ) + " descendants :"
        for d in provTree.root.descendants :
          print "goal desc : d.root ~> " + str(d.root.name) + str(d.root.record) + ", type = " + str(d.root.treeType) 

        # iterate over descendants
        for d in provTree.root.descendants :
          print "  Examining " + str(d.root.treeType) + " " + str( d.root.name ) + str( d.root.record )
          if d.root.treeType == "rule" :
            currFmla = OrFormula.OrFormula()
            currFmla.addArg( self.convertToCNF( d ) )

          elif d.root.treeType == "fact" :
            currFmla = Literal.Literal( d.root.fmlaDisplay() )

      # ------------------------------------------- #
      # case root is a rule
      # then the CNF interpretation requires AND'ing all subgoals
      elif provTree.root.treeType == "rule" :

        print "--------"
        print " RULE : " + str( provTree.root.name ) + str( provTree.root.record ) + " has " + str( len(provTree.root.descendants) ) + " descendants :"
        for d in provTree.root.descendants :
          print "rule desc : d.root ~> " + str(d.root.name) + str(d.root.record) + ", type = " + str(d.root.treeType) 

        print "> Creating AndFormula for rule " + str( provTree.root.name ) + str( provTree.root.record )
        currFmla = AndFormula.AndFormula()  # start with an empty AND formula
        # iterate over descendants
        for d in provTree.root.descendants :
          print "  Examining "+ str(d.root.treeType) + " " + str( d.root.name ) + str( d.root.record )
          currFmla.addArg( self.convertToCNF( d ) )
          tools.bp( __name__, inspect.stack()[0][3], "rule: currFmla.display() = " + currFmla.display() )

      # ------------------------------------------- #
      # case root is not an ultimate goal, fact, goal, or rule
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: Attempting to generate CNF formula from provenance tree. Hit a node which is not an UltimateGoal, fact, goal, or rule:\n" + str(provTree.root) + " is of type " + str(provTree.root.treeType) )
      # ------------------------------------------- #

    return currFmla


#########
#  EOF  #
#########
