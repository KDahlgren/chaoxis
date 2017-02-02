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

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #

DEBUG = True

class RuleNode( ) :

  #############
  #  ATTRIBS  #
  #############
  treeType    = "rule"
  ruleInfo    = None   # dictionary of all data related to the rule
  record      = None
  bindings    = []
  descendants = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, d, rec, b ) :
    self.ruleInfo = d
    self.record   = rec
    self.bindings = b

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

  ##################
  #  GET BINDINGS  #
  ##################
  def getBindings( self ) :
    return self.bindings

  #####################
  #  SET DESCENDANTS  #
  #####################
  def setDescendants( self, results, cursor ) :
    if DEBUG :
      print "self.ruleInfo = " + str(self.ruleInfo)

    for sub in self.ruleInfo :
      isNeg   = sub[0]
      name    = sub[1]
      attList = sub[2]

      # fact descendants
      if tools.isFact( name, cursor ) :
        newFactNode = DerivTree.DerivTree( name, "fact", isNeg, self.record, results, cursor, None, self.bindings )
        self.descendants.append( newFactNode )

      # goal descendants
      else :
        newGoalNode = DerivTree.DerivTree( name, "goal", isNeg, self.record, results, cursor, None, self.bindings )
        self.descendants.append( newGoalNode )


  #############
  #  IS FACT  #
  #############
  #def isFact( self, name, cursor ) :
  #  attIDsName = None
  #  cursor.execute( "SELECT attID,attName FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name == '" + str(name) + "'" )
  #  attIDsNames = cursor.fetchall()
  #  attIDsNames = tools.toAscii_multiList( attIDsNames )

  #  if DEBUG :
  #    print "in RuleNode isFact:"
  #    print "name        = " + name
  #    print "attIDsNames = " + str(attIDsNames)

  #  if attIDsNames or (name == "clock") :
  #    return True
  #  else :
  #    return False


#########
#  EOF  #
#########
