#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# **************************************** #

DEBUG = True

class RuleNode( ) :

  #############
  #  ATTRIBS  #
  #############
  treeType      = "rule"
  origRuleData  = None   # dictionary of all data related to the rule
  bindings      = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, d, b ) :
    self.origRuleData = d
    self.bindings     = b

  ########################
  #  GET ORIG RULE DATA  #
  ########################
  def getOrigRuleData( self ) :
    return self.origRuleData

  ##################
  #  GET BINDINGS  #
  ##################
  def getBindings( self ) :
    return self.bindings

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    print "RULE NODE: origRuleData = " + self.origRuleData + " ; bindings  = " + self.bindings


#########
#  EOF  #
#########
