#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

import DerivTree, RuleNode, FactNode, provTools

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
  descendants = []
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

    self.descendants = [] # needed or else creates WAAAAAY too many edges for some reason??? <.<
    self.setDescendant( )

    if DEBUG :
      print "---------------------------------------"
      print "IN GOAL NODE " + str(self.name) + ", PRINTING " + str(len(self.descendants)) + " DESCENDANTS"
      for d in self.descendants :
        print "d.root.treeType = " + str(d.root.treeType)
        print "d.root.name     = " + str(d.root.name)
        print "d.root.isNeg    = " + str(d.root.isNeg)
        print "d.root.record   = " + str(d.root.record)
      print "---------------------------------------"

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
      # ------------------------------------ #
      # handle wildcards in fact goals here

      if "__WILDCARD__" in self.record :

        # grab all partially matching records
        allPartialMatches = provTools.getPartialMatches( self.name, self.record, self.results )
        #tools.bp( __name__, inspect.stack()[0][3], " allPartialMatches = " + str(allPartialMatches) )

        for rec in allPartialMatches :
          self.spawnFact( rec )

      else :
        self.spawnFact( self.record )
      # ------------------------------------ #

    else :

      # ===================================================== #
      # handle negative goals here
      if not self.isNeg :

        # ------------------------------------ #
        # handle wildcards in non-fact goals here
        if "__WILDCARD__" in self.record :

          # grab all partially matching records
          allPartialMatches = provTools.getPartialMatches( self.name, self.record, self.results )
          #tools.bp( __name__, inspect.stack()[0][3], " allPartialMatches = " + str(allPartialMatches) )

          for rec in allPartialMatches :
            self.spawnRule( rec )
          #tools.bp( __name__, inspect.stack()[0][3], " HANLDING WILDCARD BREAKPOINT " )

        else :
          self.spawnRule( self.record )
        # ------------------------------------ #

      else :
        if DEBUG :
          print ">>> hit negative goal <<<"
      # ===================================================== #

  ################
  #  SPAWN FACT  #
  ################
  def spawnFact( self, seedRecord ) :
    #self.descendant = DerivTree.DerivTree( self.name, "fact", self.isNeg, seedRecord, self.results, self.cursor )
    self.descendants.append( DerivTree.DerivTree( self.name, "fact", self.isNeg, seedRecord, self.results, self.cursor ) )

  ################
  #  SPAWN RULE  #
  ################
  def spawnRule( self, seedRecord ) :
    self.descendant = DerivTree.DerivTree( self.name, "rule", False, seedRecord, self.results, self.cursor )


#########
#  EOF  #
#########
