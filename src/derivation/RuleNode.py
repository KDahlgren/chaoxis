#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath )
import DerivTree
from Node import Node

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #

DEBUG = True

class RuleNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  ruleInfo    = None   # dictionary of all data related to the rule
  descendants = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, ruleInfo, record , bindings ) :
    Node.__init__( self, "rule", name, record, bindings )
    self.ruleInfo = ruleInfo

  #######################
  #  CLEAR DESCENDANTS  #
  #######################
  def clearDescendants( self ) :
    self.descendants = []

  #####################
  #  GET DESCENDANTS  #
  #####################
  def getDescendants( self ) :
    return self.descendants

  ################
  #  PRINT TREE  #
  ################
  def printTree( self ) :
    print "********************************"
    print "           RULE NODE"
    print "********************************"
    print "ruleInfo :" + str( self.ruleInfo )
    print "record   :" + str( self.record   )
    print "bindings :" + str( self.bindings )
    print "[ DESCENDANTS ]"
    for d in self.descendants :
      d.printDerivTree()

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    return "RULENODE: " + str( self.ruleInfo ) + "; \nbindings = " + str( self.bindings )

  ########################
  #  GET ORIG RULE DATA  #
  ########################
  def getRuleInfo( self ) :
    return self.ruleInfo

  #####################
  #  SET DESCENDANTS  #
  #####################
  def setDescendants( self, results, cursor ) :
    if DEBUG :
      print "self.ruleInfo = " + str(self.ruleInfo)
      #sys.exit( "self.ruleInfo = " + str(self.ruleInfo) )

    for sub in self.ruleInfo :
      isNeg   = sub[0]
      name    = sub[1]
      attList = sub[2]

      if DEBUG :
        print "sub              = " + str(sub)
        print "self.descendants = " + str(self.descendants)

      # fact descendants
      if tools.isFact( name, cursor ) :
        newFactNode = DerivTree.DerivTree( name, "fact", isNeg, self.record, results, cursor, attList, self.bindings )
        self.descendants.append( newFactNode )

      # goal descendants
      else :
        newGoalNode = DerivTree.DerivTree( name, "goal", isNeg, self.record, results, cursor, attList, self.bindings )
        self.descendants.append( newGoalNode )

    if DEBUG :
      print ">>> DEBUGGING RULE INFO <<<"
      print "RULE : name = " + self.name + ", record = " + str(self.record)
      print "self.descendants = " + str(self.descendants)
      descList = self.descendants
      for desc in descList :
        print "treeType = " + desc.root.treeType
        print desc.root.printNode()
      print "********************************"

    #sys.exit( "BREAKPOINT" )

#########
#  EOF  #
#########
