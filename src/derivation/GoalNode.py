#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

import DerivTree

# **************************************** #

DEBUG = True

class GoalNode( ) :

  #############
  #  ATTRIBS  #
  #############
  treeType    = "goal"
  name        = None  # name of relation identifier
  isNeg       = False # is goal negative? assume positive
  record      = []
  descendants = []
  bindings    = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, n, i, r ) :
    self.name     = n
    self.isNeg    = i
    self.record   = r

  ################
  #  PRINT TREE  #
  ################
  def printTree( self ) :
    print "********************************"
    print "           GOAL NODE"
    print "********************************"
    print "name   :" + str( self.name )
    print "isNeg  :" + str( self.isNeg )
    print "record :" + str( self.record )
    print "[ DESCENDANTS ]"
    for d in self.descendants :
      d.printDerivTree()

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    return "GOAL NODE: \nname = " + str( self.name ) + " ; \nisNeg = " + str( self.isNeg ) + ";\nbindings = " + str(self.bindings)

  ##############
  #  GET NAME  #
  ##############
  def getName( self ) :
    return self.name

  ##############
  #  GET SIGN  #
  ##############
  def getSign( self ) :
    return self.isNeg

  ################
  #  GET RECORD  #
  ################
  def getRecord( self ) :
    return self.record

  #####################
  #  SET DESCENDANTS  #
  #####################
  def setDescendants( self, allSubs, bindings, results, cursor ) :
    self.bindings = bindings

    #sys.exit( "BREAKPOINT: allSubs = " + str( allSubs )  )

    for subDict in allSubs :
      for sname in subDict :
        subData  = subDict[ sname ]
        isNegStr = subData[0]
        subAtts  = subData[0]

        #sys.exit( "BREAKPOINT: sname = " + sname + ", subAtts = " + str(subAtts) )
        if "notin" in isNegStr :
          newRuleNode = DerivTree.DerivTree( sname, "rule", True, self.record, results, cursor, allSubs, bindings )
        else :
          newRuleNode = DerivTree.DerivTree( sname, "rule", False, self.record, results, cursor, allSubs, bindings )

        self.descendants.append( newRuleNode )


  #####################
  #  GET DESCENDANTS  #
  #####################
  def getDescendants( self ) :
    return self.descendants


#########
#  EOF  #
#########
