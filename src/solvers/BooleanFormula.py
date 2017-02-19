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
  value = None
  left  = None
  right = None
  sign  = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__(self, left=None, right=None, val=None):
    self.val = val
    self.left = left
    self.right = right
    self.sign = "UNIMPLEMENTED"


  #############
  #  __STR__  #
  #############
  # string representation of a boolean formula
  def __str__(self):

    # return val if populated
    if not self.val == None :
      return self.val

    # val empty, so return string representations of subtrees recursively
    else:
      return "(" + str(self.left) + " " + self.sign + " " + str(self.right) + ")"


  #############
  #  __CMP__  #
  #############
  # define comparison between boolean formulas
  # return 1 if different
  # return 0 if same
  def __cmp__( self, other ):

    # case no other defined
    if not other :
      return 1

    # case val of this node in the boolean formula is populated
    elif self.val :
      return cmp( self.val, other.val)

    # case val is not populated
    else :

      # case signs are identical
      if self.sign == other.sign:

        # case same left vals and same right vals
        if self.left == other.left and self.right == other.right :
          return 0

        # case different left vals or different right vals
        else:
          return 1

      # case signs are different
      else:
        return 1


  ############
  #  TO CNF  #
  ############
  # convert the boolean formula to CNF
  @abc.abstractmethod
  def toCNF( self ):
      return None


  ############
  #  IS CNF  #
  ############
  # check if already CNF
  @abc.abstractmethod
  def isCNF( self ) :
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
  # 
  def variables( self ) :

    # case val is populated, return val as a set
    if self.val is not None:
      return set([self.val])

    # case val empty, recursively grab the variables from
    # the left and right subtrees
    else:
      return self.left.variables().union(self.right.variables())


  #############
  #  CLAUSES  #
  #############
  # //
  def clauses( self ) :

    # 
    if self.val is not None:
      return 1 

    else:
       return 1 + self.left.clauses() + self.right.clauses()


  ###########
  #  DEPTH  #
  ###########
  
  def depth(self):
    if self.val is not None:
      return 1
    else:
      lft = self.left.depth()
      rgh = self.right.depth()
       if lft > rgh:
         return 1 + lft
       else:
         return 1 + rgh

  def nodeset(self):
    if self.val is not None:
      return set((self.ident(), self.val))
    else:
      sub = self.left.nodeset().union(self.right.nodeset())
      return sub.add((self.ident(), self.sign))

  def edgeset(self):
    if self.val is not None:
      return set()
    else:
      sub = self.left.edgeset().union(self.right.edgeset())
      sub.add((self.ident(), self.left.ident()))
      sub.add((self.ident(), self.right.ident()))
      return sub

  def ident(self):
    return str(self)




  ###############
  #  CONJUNCTS  #
  ###############
  # Implemented by derived classes
  @abc.abstractmethod
  def conjuncts(self):
    return None


#########
#  EOF  #
#########
#  EOF  #
