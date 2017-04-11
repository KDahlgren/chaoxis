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
    self.rootname    = name
    self.subtrees    = []
    self.fullResults = parsedResults
    self.cursor      = cursor


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
  def generateProvTree( self, name, seedRecord ) :
    return DerivTree.DerivTree( name, None, "goal", False, None, seedRecord, self.fullResults, self.cursor )
 
 
  ##################
  #  CREATE GRAPH  #
  ##################
  # input list of prov trees (DerivTree instances)
  # save image file, no return value
  def createGraph( self, addNameInfo, iter_count ) :
    if DEBUG :
      print "... running createGraph ..."
      print "subtrees = " + str( self.subtrees )
  
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
      topology   = tree.getTopology( )
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


#########
#  EOF  #
#########
