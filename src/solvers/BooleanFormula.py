#!/usr/bin/env python

'''
BooleanFormula.py
  definition of a boolean formula.
  borrows elements from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import abc, inspect, os, sys, time
from types import *
import pydot

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." )  )

from utilities import tools

# **************************************** #

DEBUG       = tools.getConfig( "SOLVERS", "BOOLEANFORMULA_DEBUG", bool )
IMGSAVEPATH = os.path.abspath( __file__  + "/../../../save_data/graphOutput" )


class BooleanFormula( object ) :

  ################
  #  ATTRIBUTES  #
  ################
  left        = None
  right       = None
  value       = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, left, right, value ) :
    __metaclass__ = abc.ABCMeta
    self.left  = left
    self.right = right
    self.value = value


  #############
  #  DISPLAY  #
  #############
  # string representation of a boolean formula
  def display( self ) :

    if DEBUG :
      print "running display:"
      print "---------------------------------------"
      print "  self             = " + str(self)
      print "  self.left        = " + str( self.left )
      print "  self.right       = " + str( self.right )
      print "  self.value       = " + str( self.value )

      if not self.value :
        print "  self.unary       = " + str( self.unary )

      print
      print "  type(self)       = " + str( type(self) )
      print "  type(self.left)  = " + str( type(self.left) )
      print "  type(self.right) = " + str( type(self.right) )
      print "  type(self.value) = " + str( type(self.value) )

      if not self.value :
        print "  type(self.unary) = " + str( type(self.unary) )

      print

    # a literal
    if self.value :
      return self.value           # <------ BASE CASE 1

    # an AND or OR formula, but with only one descendant
    elif self.unary :
      return self.unary.display()

    # both arguments exist for the formula
    elif self.left and self.right : 
      return "( " + self.left.display() + " " + self.operator + " " + self.right.display() + " )"

    elif self.left :
      return self.left.display()

    else :
      return "raw_formula_construction_NOT_WORKING =["


  ###########
  #  GRAPH  #
  ###########
  # plot the formula in a graph
  def graph( self ) :

    if DEBUG :
      print
      print
      print "------------------------"
      print "... graphing formula ..."
      print "------------------------"
      print

    # declare graph
    graph = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges
    path  = IMGSAVEPATH + "/cnfFormula_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str(time.strftime("%H"+"hrs-"+"%M"+"mins-"+"%S" +"secs" ))

    # get set of nodes
    nodes = self.nodeset()

    # get set of edges
    edges = self.edgeset()

    if DEBUG :
      print "nodes = " + str( nodes )
      print "edges = " + str( edges )

    # ------------------------------------------- #

    # prep node set
    pyNodes = []
    for node in nodes :
      pyNodes.append( pydot.Node( node ) )

    # add nodes to graph
    for n in pyNodes :
      graph.add_node( n )

    # ------------------------------------------- #

    # prep edge set
    pyEdges = []
    for edge in edges :

      if DEBUG :
        print "edge[0] = " + str( edge[0] )
        print "edge[1] = " + str( edge[1] )

      pyEdges.append( pydot.Edge( edge[0], edge[1] ) )

    # add nodes to graph
    for e in pyEdges :
      if DEBUG :
        print "e = " + str( e )
      #graph.add_edge( n )

    # ------------------------------------------- #
 
    #graph.write_png( path + '.png' )


  ##############
  #  NODE SET  #
  ##############
  # get the nodeset representation of the formula
  # supports formula plot code for sanity checking.
  def nodeset( self ) :

    # the nodeset of a Literal is the value
    if self.value :
      return [ self.value ]

    # the nodeset of a unary is the nodeset of the unary
    elif self.unary :
      return self.unary.nodeset()

    # the nodeset of a fmla in which both arguments exist
    # is the union of the left and the right node sets
    elif self.left and self.right :

      if DEBUG :
        print "self.left.nodeset()  = " + str( self.left.nodeset() )
        print "self.right.nodeset() = " + str( self.right.nodeset() )

      # populate left set
      leftNodes  = set( self.left.nodeset() )

      # populate right set
      rightNodes = set( self.right.nodeset() )

      # return union
      return leftNodes.union( rightNodes )

    elif self.left :
      return self.left.nodeset()

    elif self.right :
      return self.right.nodeset()

    else :
      return "Somethin's broken in nodeset() =["


  ##############
  #  EDGE SET  #
  ##############
  # get the edgeset representation of the formula
  # supports formula plot code for sanity checking.
  def edgeset( self ) :

    # the edgeset of a Literal is nothing
    if self.value :
      return ()

    # the edgeset of a unary is the edgeset of the unary
    elif self.unary :
      return self.unary.edgeset()
      
    # the edgeset of a fmla in which both arguments exist
    # is the union of the left and the right edge sets
    elif self.left and self.right :

      if DEBUG :
        print "self.left.display()  = " + str( self.left.display() )
        print "self.right.display() = " + str( self.right.display() )
        print "self.left.edgeset()  = " + str( self.left.edgeset() )
        print "self.right.edgeset() = " + str( self.right.edgeset() )

      # populate with left edges
      existingEdges_left = self.left.edgeset()
      newEdge_left       = ( self.display(), existingEdges_left )

      # populate with right edges
      existingEdges_right = self.right.edgeset()
      newEdge_right       = ( self.display(), existingEdges_right )

      if DEBUG :
        print "newEdge_left  = " + str( newEdge_left )
        print "newEdge_right = " + str( newEdge_right )

      completeEdgeSet = [ newEdge_left, newEdge_left ]
      return completeEdgeSet

    elif self.left :
      return self.left.edgeset()

    elif self.right :
      return self.right.edgeset()

    else :
      return "Somethin's broken in edgeset() =["


#########
#  EOF  #
#########
