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
  def setDescendants( self, allRules, bindings, results, cursor ) :
    self.bindings = bindings
    for rule in allRules :
      rid     = rule[0]
      rname   = rule[1]
      subinfo = rule[2]

      for rule in allRules :
        if DEBUG :
          print "rule = " + str(rule)

        newRuleNode = DerivTree.DerivTree( rname, "rule", False, self.record, results, cursor, rule, bindings )
        self.descendants.append( newRuleNode )

    return None

  #####################
  #  GET DESCENDANTS  #
  #####################
  def getDescendants( self ) :
    return self.descendants

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    print "GOAL NODE: \nname = " + self.name + " ; \nisNeg = " + self.isNeg + " ; \nrecord = " + self.record + ";\ndescendants = " + self.descendants + ";\nbindings = " + str(self.bindings)


#########
#  EOF  #
#########
