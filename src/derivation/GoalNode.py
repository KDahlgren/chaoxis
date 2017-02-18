#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

import DerivTree, RuleNode, FactNode

packagePath1  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath1 )
from Node import Node

packagePath2  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath2 )
from utils import tools

# **************************************** #

DEBUG = True

class GoalNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  descendant = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record, results, cursor ) :

    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "goal", name, isNeg, record, results, cursor )

    if DEBUG :
      print "<><><><><><><><><><><><><><><><><><><>"
      print "CREATING GOAL FOR : "
      print "  self.name   = " + str(self.name )
      print "  self.isNeg  = " + str( self.isNeg )
      print "  self.record = " + str( self.record )
      print "<><><><><><><><><><><><><><><><><><><>"

    self.setDescendant( )


  #############
  #  __STR__  #
  #############
  # the string representation of a GoalNode
  def __str__( self ) :
    if self.isNeg :
      negStr = "_NOT_"
      return negStr + " " + self.name + "(" + str(self.record) + ")"
    else :
      return self.name + "(" + str(self.record) + ")"

  #############
  #  DISPLAY  #
  #############
  # the string representation of a GoalNode
  def display( self ) :
    myStr = None

    if self.isNeg :
      negStr = "_NOT_ "
      myStr =  negStr + "," + self.name + "(" + str(self.record) + ")"

    else :
      myStr = self.name + "(" + str(self.record) + ")"

    return str( myStr )

  ####################
  #  SET DESCENDANT  #
  ####################
  # goal nodes have exactly one descendant, either a single rule node or a single fact node.
  def setDescendant( self ) :

    if DEBUG :
      print "self.name                              = " + self.name
      print "self.isNeg                             = " + str( self.isNeg )
      print "self.record                            = " + str( self.record )
      print "tools.isFact( self.name, self.cursor ) = " + str( tools.isFact( self.name, self.cursor ) )

    if tools.isFact( self.name, self.cursor ) :
      self.descendant = DerivTree.DerivTree( self.name, "fact", self.isNeg, self.record, self.results, self.cursor )

    else :
      if not self.isNeg :
        self.descendant = DerivTree.DerivTree( self.name, "rule", False, self.record, self.results, self.cursor )


#########
#  EOF  #
#########
