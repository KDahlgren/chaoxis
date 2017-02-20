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
import inspect, os, sys
import abc, random

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


class BooleanFormula :

  ################
  #  ATTRIBUTES  #
  ################
  value    = None
  left     = None
  right    = None
  operator = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__(self, left=None, right=None, val=None):
    self.val      = val
    self.left     = left
    self.right    = right
    self.operator = "UNIMPLEMENTED"


  #############
  #  __STR__  #
  #############
  # string representation of a boolean formula
  def __str__(self):

    # return val if populated
    if not self.val == None :
      return self.val

    # val empty
    # (boolean formula is not a literal)
    # return string representations of subtrees recursively
    else:
      return "(" + str(self.left) + " " + self.operator + " " + str(self.right) + ")"


  #############
  #  __CMP__  #
  #############
  # define comparison between boolean formulas
  # return 1 if different
  # return 0 if same
  def __cmp__( self, other ):

    # case no other defined
    # essentially a no-op
    if not other :
      return 1

    # case val of this node in the boolean formula is populated
    # boolean formula has no operators. it's a literal.
    elif self.val :
      return cmp( self.val, other.val)

    # case val is not populated
    # (boolean formula is not a literal)
    else :

      # case operators are identical
      if self.operator == other.operator :

        # case same left vals and same right vals
        if self.left == other.left and self.right == other.right :
          return 0

        # case different left vals or different right vals
        else:
          return 1

      # case operators are different
      else:
        return 1


  ############
  #  TO CNF  #
  ############
  # convert the boolean formula to CNF
  # Implemented by derived classes
  @abc.abstractmethod
  def toCNF( self ):
      return None


  ############
  #  IS CNF  #
  ############
  # check if already CNF
  # Implemented by derived classes
  @abc.abstractmethod
  def isCNF( self ) :
      return None


  ###############
  #  CONJUNCTS  #
  ###############
  # Implemented by derived classes
  @abc.abstractmethod
  def conjuncts( self ) :
    return None


  ###########
  #  GRAPH  #
  ###########
  # plot the formula in a graph
  def graph(self, file):
    #dot = Digraph(comment="LDFI", format='png')
    #edges = self.edgeset()

    #dot.edges(edges)
    #dot.render(file)
    tools.bp( __name__, inspect.stack()[0][3], "TODO: Implement boolean formula plotting.")


  ###############
  #  VARIABLES  #
  ###############
  # get the complete set of variables in this boolean formula
  def variables( self ) :

    # case val is populated, return val as a set
    if self.val is not None:
      return set([self.val])

    # case val empty
    # (boolean formula is not a literal)
    # recursively grab the variables from
    # the left and right subtrees
    else:
      return self.left.variables().union(self.right.variables())


  #############
  #  CLAUSES  #
  #############
  # count the number of clauses in this boolean formula
  def clauses( self ) :

    # val is populated
    if self.val is not None:
      return 1 

    # val is not populated
    # (boolean formula is not a literal)
    else:
       return 1 + self.left.clauses() + self.right.clauses()


  ###########
  #  DEPTH  #
  ###########
  # get the depth of the formula tree representation
  def depth( self ) :

    # val is populated
    if self.val is not None:
      return 1

    # (boolean formula is not a literal)
    # recursively calculate the depth from left and right 
    # arguments of the operator
    else:
      lft = self.left.depth()
      rgh = self.right.depth()
       if lft > rgh:
         return 1 + lft
       else:
         return 1 + rgh


  ##############
  #  NODE SET  #
  ##############
  # get the nodeset representation of the formula
  # supports formula plot code for sanity checking.
  def nodeset( self ) :

    # case val is populated
    if self.val is not None :
      return set( str( self ), self.val )

    # case val is empty
    # (boolean formula is not a literal)
    # return the left and right node sets recursively,
    # while adding the node.
    else:
      sub = self.left.nodeset().union(self.right.nodeset())
      return sub.add( ( str( self ), self.operator ) ) # nodes are tuples


  ##############
  #  EDGE SET  #
  ##############
  # get the edgeset representation of the formula
  # supports formula plot code for sanity checking.
  def edgeset( self ) :

    # case val is populated
    if self.val is not None:
      return set()

    # case val is empty
    # (boolean formula is not a literal)
    # return edgesets of left and right equations recursively.
    else:
      sub = self.left.edgeset().union(self.right.edgeset())
      sub.add( str( self ), str( self.left  ) )
      sub.add( str( self ), str( self.right ) )
      return sub


#########
#  EOF  #
#########
