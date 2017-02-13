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
  def __init__( self, name, ruleInfo, record , bindings, cursor ) :
    Node.__init__( self, "rule", name, record, bindings, cursor )
    self.ruleInfo = ruleInfo
    self.schemaBindings = []
    self.setBindings( bindings )
    #sys.exit( "BREAKPOINT: schemaBindings = " + str(self.schemaBindings) )

  ##################
  #  SET BINDINGS  #
  ##################
  def setBindings( self, allBindings ) :
    #sys.exit( "BREAKPOINT: \nschema = " + str(self.schema) + "\nallBindings = " + str(allBindings) )

    print "self.schema = " + str(self.schema)
    print "allBindings = " + str(allBindings)
    thisSchema = self.schema
    for attS in thisSchema :
      print "attS = " + attS
      for attTup in allBindings :
        print "attTup = " + str(attTup)
        attName = attTup[0]
        attVal  = attTup[1]
        if attName in attS :
          self.schemaBindings.append( ( attS, attVal ) )

    self.schemaBindings = self.deduplicate_bindings( self.schemaBindings )
    #self.schemaBindings = list( set(self.schemaBindings) ) # ??? why needed ???
    #if self.name.startswith( "log_prov" ) :
    #  sys.exit( "BREAKPOINT: schemaBindings = " + str(self.schemaBindings) )


  ##########################
  #  DEDUPLICATE BINDINGS  #
  ##########################
  def deduplicate_bindings( self, schemaBinds ) :
    cleanList = []
    for bind in schemaBinds :
      if not bind in cleanList :
        cleanList.append( bind )
    return cleanList


  #######################
  #  CLEAR DESCENDANTS  #
  #######################
  def clearDescendants( self ) :
    self.descendants = []

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

      # clean name if necessary
      if "-makeunique-" in name :
        n = name.split( "-makeunique-" )
        name = n[0]

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
