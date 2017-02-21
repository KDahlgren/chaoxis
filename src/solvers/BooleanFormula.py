#!/usr/bin/env python

'''
BooleanFormula.py
  definition of a boolean formula.
  borrows heavily from https://github.com/palvaro/ldfi-py
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
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


IMGSAVEPATH = os.path.abspath( __file__  + "/../../../save_data/graphOutput" )


class BooleanFormula( object ) :

  ################
  #  ATTRIBUTES  #
  ################
  value    = None
  left     = None
  right    = None
  operator = None
  isEmpty  = False # an empty formula subtree


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, left, right, value ) :
    self.left     = left
    self.right    = right
    self.value    = value


  #############
  #  DISPLAY  #
  #############
  # string representation of a boolean formula
  def display( self ) :

    print "---------------------------------------"
    print "  self             = " + str(self)
    print "  self.left        = " + str( self.left )
    print "  self.right       = " + str( self.right )
    print "  type(self)       = " + str( type(self) )
    print "  type(self.left)  = " + str( type(self.left) )
    print "  type(self.right) = " + str( type(self.right) )


    # case both left and right arguments are populated
    if self.left and self.right :
      return "(" + self.left.display() + " " + self.operator + " " + self.right.display() + ")"
      #return "(" + self.left.display() + " " + self.operator + " " + str( self.right.display() ) + ")"

    # case right argument is not populated
    elif self.left and self.right == None :
      return self.left.display()

    # case left argument is not populated
    elif self.left == None and self.right :
      return self.right.display()

    elif self.left == None and self.right == None :
      return "HIT SOME SHIT"


  ###########
  #  GRAPH  #
  ###########
  # plot the formula in a graph
  def graph( self ) :

    # declare graph
    graph = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges
    path  = IMGSAVEPATH + "/cnfFormula_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str(time.strftime("%H"+"hrs-"+"%M"+"mins-"+"%S" +"secs" ))

    # get set of nodes
    nodes = self.nodeset()

    # get set of edges
    #edges = self.edgeset()

    #if DEBUG :
    #  print "nodes = " + str( nodes )
    #  print "edges = " + str( edges )
    #  tools.bp( __name__, inspect.stack()[0][3], "breakpoint here." )   
 
    #graph.write_png( path + '.png' )


  ##############
  #  NODE SET  #
  ##############
  # get the nodeset representation of the formula
  # supports formula plot code for sanity checking.
  def nodeset( self ) :

    # case value is populated
    if self.isLiteral() :
      #tools.bp( __name__, inspect.stack()[0][3], "yes is literal" )
      return set( [ self.value ] )

    # case val is empty
    # (boolean formula is not a literal)
    # return the left and right node sets recursively,
    # while adding the node.
    else:
      #tools.bp( __name__, inspect.stack()[0][3], "not literal" )
      #tools.bp( __name__, inspect.stack()[0][3], "str(self) = " + str(self) )


      if self.left == None and self.right == None :
        return set( [ self.val ] )

      if self.left == None or self.right == None :
        print "str( self )  = " + str( self )
        print "type( self ) = " + str( type( self ) )
        tools.bp( __name__, inspect.stack()[0][3], "\nself.left = " + str(self.left) + "\nself.right = " + str(self.right) )

      print "self.left.nodeset()  = " + str( self.left.nodeset() )
      print "self.right.nodeset() = " + str( self.right.nodeset() )

      sub = self.left.nodeset().union( self.right.nodeset() )
      #return sub.add( ( str( self ), self.operator ) ) # nodes are tuples


  ##############
  #  EDGE SET  #
  ##############
  # get the edgeset representation of the formula
  # supports formula plot code for sanity checking.
  def edgeset( self ) :

    # case val is populated
    if self.isLiteral() :
      return set()

    # case val is empty
    # (boolean formula is not a literal)
    # return edgesets of left and right equations recursively.
    else:
      sub = self.left.edgeset().union( self.right.edgeset() )
      sub.add( ( str( self ), str( self.left  ) ) )
      sub.add( ( str( self ), str( self.right ) ) )
      return sub


#########
#  EOF  #
#########
