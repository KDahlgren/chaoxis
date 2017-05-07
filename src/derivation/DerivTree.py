#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, string, sys
import pydot

# ------------------------------------------------------ #
import GoalNode, RuleNode, FactNode, provTools

# ------------------------------------------------------ #

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #


DEBUG = False

# --------------------------------------------------- #
#                   DERIV TREE CLASS                  #
# --------------------------------------------------- #
class DerivTree( ) :

  #############
  #  ATTRIBS  #
  #############
  name           = None # name of relation identifier
  rid            = None # rule id, if applicable
  treeType       = None # goal, rule, or fact
  isNeg          = None # is goal negative? assume positive
  root           = None # GoalNode, RuleNode, FactNode
  programResults = None # complete dictionary of parsed results from table dump
  cursor         = None # database pointer
  provAttMap     = None
  idPair         = None

  ####################
  #  IS FINAL STATE  #
  ####################
  # a convenience function
  # ProvTrees are not DerivTrees
  def isFinalState( self ) :
    return False


  #############
  #  IS LEAF  #
  #############
  # a convenience function
  # a DeriveTree is a leaf iff it is rooted at a fact.
  def isLeaf( self ) :
    if self.root.treeType == "fact" :
      return True
    else :
      return False

  # ------------------------------------------ #
  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, rid, treeType, isNeg, provAttMap, record, results, cursor ) :

    self.name           = name
    self.rid            = rid
    self.treeType       = treeType
    self.isNeg          = isNeg
    self.programResults = results
    self.cursor         = cursor
    self.provAttMap     = provAttMap

    if DEBUG :
      print "=================================="
      print "       CREATING NEW DERIV TREE"
      print " self.name     = " + str( self.name )
      print " self.treeType = " + str( self.treeType )
      print " self.isNeg    = " + str( self.isNeg )
      print "=================================="

    self.generateDerivTree( record )

  # ------------------------------------------ #
  #########################
  #  GENERATE DERIV TREE  #
  #########################
  def generateDerivTree( self, record ) :

    if self.treeType == "goal" :
      self.root = GoalNode.GoalNode( self.name, self.isNeg, record, self.programResults, self.cursor )

    elif self.treeType == "rule" :
      self.root = RuleNode.RuleNode( self.name, self.rid, self.provAttMap, record, self.programResults, self.cursor )

    elif self.treeType == "fact" :
      self.root = FactNode.FactNode( self.name, self.isNeg, record, self.programResults, self.cursor )

    else :
      self.errorMsg1()

  # ------------------------------------------ #
  ##################
  #  GET TOPOLOGY  #
  ##################
  def getTopology( self ) :
    nodes = []
    edges = []

    if DEBUG :
      print "***************************************"
      print "self.root.treeType = " + self.root.treeType
      print "str(self.root)     = " + str( self.root )
      print "***************************************"

    thisNode = provTools.createNode( self.root ) # prepare this node.
    nodes.append( thisNode )                # add this node to the topology

    # recursively ask for all descendant nodes.
    if not self.root.treeType == "fact" : # facts have no descendants

      # ----------------------------------- #
      # case goal
      if self.root.treeType == "goal" :

        if not self.root.descendants == [] :
          desc = self.root.descendants

        else :
          return ( nodes, edges ) # this goal node has no descendants ( change when supporting negation )

      # ----------------------------------- #
      # case rule
      elif self.root.treeType == "rule" :
        desc = self.root.descendants    # rules have one or many descendants

      # ----------------------------------- #
      if DEBUG :
        print "desc = " + str(desc)
        for d in desc :
          print "d.root.name     = " + str( d.root.name )
          print "d.root.treeType = " + str( d.root.treeType )

      # ----------------------------------- #
      # iterate over descendants
      for d in desc :
        # prepare the node 
        # (kind of redundant since it will be created again in the next recursive step)
        descendantNode = provTools.createNode( d.root )
 
        # create an edge
        edges.append( pydot.Edge( thisNode, descendantNode ) )

        # update topology with recursive results
        topo = d.getTopology()
        nodes.extend( topo[0] )
        edges.extend( topo[1] )

    return ( nodes, edges )


  # ------------------------------------------ #
  ############################
  #  GET TOPOLOGY EDGE SET   #
  ############################
  def getTopology_edgeSet( self ) :
    edges = []

    # recursively ask for all descendant nodes.
    if not self.root.treeType == "fact" : # facts have no descendants

      # ----------------------------------- #
      # case goal
      if self.root.treeType == "goal" :

        if not self.root.descendants == [] :
          desc = self.root.descendants

        else :
          return edges

      # ----------------------------------- #
      # case rule
      elif self.root.treeType == "rule" :
        desc = self.root.descendants    # rules have one or many descendants

      # ----------------------------------- #
      # iterate over descendants
      for d in desc :

        # create an edge
        edges.append( ( str( self.root ), str( d.root ) ) )

        # update topology with recursive results
        edges.extend( d.getTopology_edgeSet() )

    return edges


  # ------------------------------------------ #
  #################
  #  ERROR MSG 1  #
  #################
  def errorMsg1( self ) :
    sys.exit( "***** FATAL ERROR *****\nWe regret to inform you the universe has imploded as a result of attempting to create a provenance tree using an unrecognized node type, '" + self.treeType + "', as specified by the appended initialization data, which is not one of the hallowed tree node types, specifically 'goal', 'rule', or 'fact'. Please travel back in time and try again.\nOffending initialization data:\n" + "name = " + self.name + "\ntreeType = " + self.treeType + "\nisNeg = " + str( self.isNeg ) + "\nprogramResults = " + str( self.programResults ) + "\ncursor = " + str( self.cursor )   )


#########
#  EOF  #
#########
