#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import time
import os, sys
import graphviz, functools

# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath )

import DerivTree, GoalNode, RuleNode, FactNode

# **************************************** #

DEBUG       = True
IMGSAVEPATH = os.path.abspath( __file__  + "/../../../save_data/graphvizOutput" )

# --------------------------------------------------- #

class ProvTree() :

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

  ########################
  #  GENERATE PROV TREE  #
  ########################
  def generateProvTree( self, seedRecord ) :
    return DerivTree.DerivTree( "post", "goal", False, seedRecord, self.fullResults, self.cursor, None, None )
  
  ##################
  #  CREATE GRAPH  #
  ##################
  # input list of prov trees (DerivTree instances)
  # save image file, no return value
  def createGraph( self ) :
    if DEBUG :
      print "... running createGraph ..."
      print "subtrees = " + str( self.subtrees )
  
    graph = functools.partial( graphviz.Graph, format='jpg' )
    path  = IMGSAVEPATH + "/provtree_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str(time.strftime("%H-%M-%S"))
    nodes = []
    edges = []
    for tree in self.subtrees :
      #edges.append( ( self.rootname, tree.root ) )
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
  
    # convert tuples to strings
    nodes_str = []
    nodes_str.append( self.rootname )
    for n in nodes :
      nodes_str.append( n[0] + ", "  + n[1] )
    print "nodes_str = " + str(nodes_str)
  
    edges_str = []
    for edge in edges :
      print "edge = " + str(edge)
      edge_str_0 = edge[0][0] + ", " + edge[0][1]
      edge_str_1 = edge[1][0] + ", " + edge[1][1]
      edges_str.append( (edge_str_0, edge_str_1) )
      # add edges from ultimate goal to post goals for aesthetics
      if ( edge[0][0] == "goal" ) and ( edge[0][1].startswith( "post[" ) ) :
        edges_str.append( ( self.rootname, edge_str_0 ) )
    print "edges_str = " + str(edges_str)
  
    # create graph
    g          = self.add_nodes( graph(), nodes_str )
    g_complete = self.add_edges( g, edges_str )
    print "Saving prov tree render to " + str(path)
    g_complete.render( path )

  # --------------------------------------------------- #
  # --------------------------------------------------- #

  # add_nodes and add_edges borrowed from tutorial: http://matthiaseisen.com/articles/graphviz/
  def add_nodes(self, graph, nodes):
      for n in nodes:
          if isinstance(n, tuple):
              graph.node(n[0], **n[1])
          else:
              graph.node(n)
      return graph
 
  def add_edges(self, graph, edges):
      for e in edges:
          if isinstance(e[0], tuple):
              graph.edge(*e[0], **e[1])
          else:
              graph.edge(*e)
      return graph
 
  # --------------------------------------------------- #
  # --------------------------------------------------- #

#########
#  EOF  #
#########
