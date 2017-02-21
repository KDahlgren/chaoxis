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
    self.formula  = self.convertToCNF( self.provTree )


  ####################
  #  CONVERT TO CNF  #
  ####################
  # recursively construct a CNF formula from the given prov tree
  def convertToCNF( self, provTree ) :

    if not provTree.isUltimateGoal() and provTree.root.name == "bcast" :
      print "...> processing " + provTree.root.name

    currFmla = None  # initialize current formula

    if DEBUG :
      print "*************************************************"
      print "****> running convertToCNF in function " + inspect.stack()[0][3] + " in file " + __name__

    # ------------------------------------------- #
    #        BASE CASE : provTree is a fact       #
    # ------------------------------------------- #
    if provTree.isLeaf( ) :

      if DEBUG :
        if provTree.root.name == "bcast" :
          print "...> " + provTree.root.name + " isLeaf"

      if provTree.treeType == "fact" :

        if DEBUG :
          print " provTree is a fact..."
          print " before: currFmla = " + str( currFmla )

        currFmla = Literal.Literal( provTree.root.fmlaDisplay() )

        if DEBUG :
          print " after: currFmla = " + str( currFmla )

    else :
      # ------------------------------------------- #
      # case prov tree is rooted at an ultimate goal
      # then the CNF interpretation requires AND'ing all subgoals
      if provTree.isUltimateGoal( ) :

        if DEBUG :
          print "...> processing UltimateGoal"

        currFmla = AndFormula.AndFormula( )  # start with an empty AND formula

        if DEBUG :
          print " provTree is an UltimateGoal..."
          print " before: currFmla = " + str( currFmla )

        it = 0
        # add CNF formulas of subtrees as args in this AND formula
        for subtree in provTree.subtrees :

          if DEBUG :
            print "================================================="
            print " subtree for loop iteration = "  + str( it )
            print " subtree.root.treeType = " + str( subtree.root.treeType ) 
            print " subtree.root.name     = " + str( subtree.root.name ) 
            print " subtree.root.record   = " + str( subtree.root.record )

          currFmla.addArg( self.convertToCNF( subtree ) )
          it += 1

        if DEBUG :
          print " done processing UltimateGoal."
          print " after: currFmla = " + str( currFmla )

      # ------------------------------------------- #
      # case root is a goal
      # then the CNF interpretation requires OR'ing all contributing rules
      elif provTree.root.treeType == "goal" :

        currFmla = OrFormula.OrFormula( )  # start with an empty OR formula

        if DEBUG :
          print "...> processing goal " + str( provTree.root.name )
          print "     before: currFmla = " + str( currFmla )

        # iterate over descendants
        for d in provTree.root.descendants :
          currFmla.addArg( self.convertToCNF( d ) )

        if DEBUG :
          print "     after: currFmla = " + str( currFmla )
          if str(currFmla.fmla) == "bcast(['a', 'hello', '1'])" :
            print "currFmla       = " + str( currFmla )
            print "currFmla.fmla  = " + str( currFmla.fmla )
            print "currFmla.left  = " + str( currFmla.left )
            print "currFmla.right = " + str( currFmla.right )
            #tools.bp( __name__, inspect.stack()[0][3], "breakpoint")

      # ------------------------------------------- #
      # case root is a rule
      # then the CNF interpretation requires AND'ing all subgoals
      elif provTree.root.treeType == "rule" :

        currFmla = AndFormula.AndFormula( )  # start with an empty AND formula

        if DEBUG :
          print "...> processing rule " + str( provTree.root.name )
          print "     before: currFmla = " + str( currFmla )

        # iterate over descendants
        for d in provTree.root.descendants :
          currFmla.addArg( self.convertToCNF( d ) )

        if DEBUG :
          print "     after: currFmla = " + str( currFmla )

      # ------------------------------------------- #
      # case root is not an ultimate goal, fact, goal, or rule
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: Attempting to generate CNF formula from provenance tree. Hit a node which is not an UltimateGoal, fact, goal, or rule:\n" + str(provTree.root) + " is of type " + str(provTree.root.treeType) )
      # ------------------------------------------- #

    return currFmla


#########
#  EOF  #
#########
