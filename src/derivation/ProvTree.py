#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, time
import pydot

# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath )

import DerivTree, GoalNode, RuleNode, FactNode, provTools

# **************************************** #

DEBUG       = True
IMGSAVEPATH = os.path.abspath( __file__  + "/../../../save_data/graphOutput" )

# --------------------------------------------------- #

class ProvTree( ) :

  #############
  #  ATTRIBS  #
  #############
  rootname      = None
  subtrees      = None
  parsedResults = None
  cursor        = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, parsedResults, cursor ) :
    self.rootname      = name
    self.subtrees      = []
    self.parsedResults = parsedResults
    self.cursor        = cursor


  ######################
  #  IS ULTIMATE GOAL  #
  ######################
  # a convenience function
  # a provenance tree will never not be rooted
  # at "FinalState"
  def isFinalState( self ) :
    if self.rootname == "FinalState" :
      return True
    else :
      return False


  #############
  #  IS LEAF  #
  #############
  # a convenience function
  # a non-empty provenance tree will never be a leaf.
  def isLeaf( self ) :
    return False


  ########################
  #  GENERATE PROV TREE  #
  ########################
  # populates self.subtrees
  def generateProvTree( self, name, seedRecord ) :
    return DerivTree.DerivTree( name, None, "goal", False, None, seedRecord, self.parsedResults, self.cursor )
 

  #################
  #  MERGE TREES  #
  #################
  # old_provTree := a ProvTree instance
  def mergeTrees( self, old_provTree ) :

    # define structure of the new merged tree
    merged_name          = self.rootname
    merged_subtrees      = self.subtrees.extend( old_provTree.subtrees )
    merged_parsedResults = self.parsedResults.extend( old_provTree.parsedResults )
    merged_cursor        = self.cursor

    # instantiate new ProvTree
    provTree_merged = ProvTree( self.rootname, merged_name, merged_parsedResults, merged_cursor )

    # manually construct subtrees for new merged instance
    provTree_merged.subtrees = merged_subtrees

    sys.exit( "provTree_merged.subtrees = " + str(provTree_merged.subtrees) )

    return provTree_merged

 
  ##################
  #  CREATE GRAPH  #
  ##################
  # input list of prov trees (DerivTree instances)
  # save image file, no return value
  def createGraph( self, addNameInfo, iter_count ) :
    if DEBUG :
      print "... running createGraph ..."
      print "subtrees   = " + str( self.subtrees )
      print "iter_count = " + str( iter_count )
  
    graph = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges

    path  = IMGSAVEPATH + "/provtree_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str( time.strftime( "%H"+"hrs-"+"%M"+"mins-"+"%S" +"secs" )) + "_" + str(iter_count)

    # example: add "_buggyGraph" to the end of the name
    if addNameInfo :
      path += "_" + addNameInfo

    nodes = []
    edges = []

    # add prov tree root
    provRootNode = pydot.Node( self.rootname, shape='doublecircle', margin=0 )
    nodes.append( provRootNode )

    for tree in self.subtrees :
      edges.append( pydot.Edge( provRootNode, provTools.createNode( tree.root ) ) )
      topology = tree.getTopology( )
      nodes.extend( topology[0] )
      edges.extend( topology[1] )

  
    if DEBUG :
      print "... in createGraph :" 
      print "nodes : " + str(len(nodes))
      for i in range(0,len(nodes)) :
        print "node#" + str(i) + " : " + str(nodes[i])
      print "edges : " + str(len(edges))
      for i in range(0,len(edges)) :
        print "edge#" + str(i) + " : " + str(edges[i])
  
    # create graph
    # add nodes :
    for n in nodes :
      graph.add_node( n )
    # add edges
    for e in edges :
      graph.add_edge( e )

    print "Saving prov tree render to " + str(path)
    graph.write_png( path + ".png" )


  ##################
  #  GET EDGE SET  #
  ##################
  # grab the complete list of edges for a prov tree
  # use for equality comparisons
  def getEdgeSet( self ) :
    if DEBUG :
      print "... running getEdgeSet ..."
      print "subtrees = " + str( self.subtrees )

    edgeSet = []

    for tree in self.subtrees :
      edgeSet.append( ( self.rootname, str( tree.root ) ) )
      edgeSet.extend( tree.getTopology_edgeSet() )

    return edgeSet

#########
#  EOF  #
#########
