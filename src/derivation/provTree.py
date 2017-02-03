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
IMGSAVEPATH = os.path.abspath( __file__  + "/../../../save_data" )

# --------------------------------------------------- #

########################
#  GENERATE PROV TREE  #
########################
def generateProvTree( seedRecord, fullResults, cursor ) :
  return DerivTree.DerivTree( "post", "goal", False, seedRecord, fullResults, cursor, None, None )

# --------------------------------------------------- #

# add_nodes and add_edges borrowed from tutorial: http://matthiaseisen.com/articles/graphviz/
def add_nodes(graph, nodes):
    for n in nodes:
        if isinstance(n, tuple):
            graph.node(n[0], **n[1])
        else:
            graph.node(n)
    return graph

def add_edges(graph, edges):
    for e in edges:
        if isinstance(e[0], tuple):
            graph.edge(*e[0], **e[1])
        else:
            graph.edge(*e)
    return graph

##################
#  CREATE GRAPH  #
##################
# input list of prov trees (DerivTree instances)
# save image file, no return value
def createGraph( provTreeList ) :
  if DEBUG :
    print "... running createGraph ..."

  graph = functools.partial( graphviz.Graph, format='jpg' )
  path = IMGSAVEPATH + "/provtree_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str(time.strftime("%H-%M-%S"))
  for tree in provTreeList :
    topology   = tree.getTopology( [], [] )
    nodes      = topology[0]
    edges      = topology[1]

  if DEBUG :
    print "... in createGraph :" 
    print "nodes : " + str(len(nodes))
    for i in range(0,len(nodes)) :
      print "node#" + str(i) + " : " + str(nodes[i])
    print "edges : " + str(len(edges))
    for i in range(0,len(edges)) :
      print "edge#" + str(i) + " : " + str(edges[i])

    #g          = add_nodes( graph(), nodes )
    #g_complete = add_edges( g, edges )
    #print "Saving prov tree render to " + str(path)
    #g_complete.render( path )

# --------------------------------------------------- #


#########
#  EOF  #
#########
