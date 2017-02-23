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
import pydot

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #

DEBUG = True
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

    # both arguments exist
    elif self.left and self.right : 
      return "( " + self.left.display() + " " + self.operator + " " + self.right.display() + " )"

    else :
      return "CNF_formula_construction_NOT_WORKING =["


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
