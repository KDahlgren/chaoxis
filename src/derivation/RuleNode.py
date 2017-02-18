#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

import DerivTree, provTools, GoalNode, FactNode

packagePath1  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath1 )
from Node import Node

packagePath2  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath2 )
from utils import tools

# **************************************** #

DEBUG = True

class RuleNode( Node ) :

  # --------------------------------- #

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  descendants = []

  # the rule identifier (rid/RID) of this instance of the rule.
  thisProvRID  = None
  thisProvName = None

  # the string representation of the original rule (not the provenance version)
  thisFullRuleStr = None

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, record, results, cursor ) :
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, db cursor
    Node.__init__( self, "rule", name, False, record, results, cursor )

    self.descendants = [] # needed for some reason??? <.<

    if DEBUG :
      print "*************************************"
      print "    RULE NODE INIT DATA"
      print "  name   = " + str( name )
      print "  record = " + str( record )
      print "*************************************"

    prov_rid_info = provTools.get_prov_rid_info( self.name, self.record, self.results, self.cursor )
    #sys.exit( "BREKAPOINT : provRID = " + str(self.provRID) )
    self.thisProvRID  = prov_rid_info[0]
    self.thisProvName = prov_rid_info[1]

    self.setDescendants( )

    if DEBUG :
      print "RULE NODE " + str( self.name ) + str(self.record) + " has " + str( len( self.descendants ) ) + " descendants.>"
      for d in self.descendants :
        print "   d = " + str( d.root )

  #############
  #  __STR__  #
  #############
  # the string representation of a RuleNode
  def __str__( self ) :

    # get original rule name
    tmp = self.thisProvName.split( "_prov" )
    origRuleName = tmp[0]
    #self.thisFullRuleStr = provTools.getFullRuleStr( thisProvRID, origRuleName )

    #return self.thisFullRuleStr
    return "rule-> "+ origRuleName + "(" + str(self.record) + ")"


  #####################
  #  SET DESCENDANTS  #
  #####################
  # rule nodes have one or more descendants.
  # all descendants are goal nodes.
  def setDescendants( self ) :

    goalAttMap = provTools.getGoalAttMap( self.thisProvRID, self.thisProvName, self.record, self.results, self.cursor )
    #sys.exit( "BREAKPOINT2 : goalAttMap = " + str(goalAttMap) )
    subgoals   = provTools.getSubgoals( self.thisProvRID, self.cursor )
    #sys.exit( "BREAKPOINT2 : subgoals = " + str(subgoals) )

    collectedSubMaps = []
    for sub in subgoals :
      subName = sub[0]
      isNeg   = sub[1]
      attList = sub[2]

      # get sub att map
      subAttMap = provTools.getSubAttMap( subName, attList, goalAttMap )
      collectedSubMaps.append( (subName, isNeg, subAttMap) )

    #if self.thisProvName.startswith( "post_prov" ) :
    #  tools.bp( __name__, inspect.stack()[0][3], "collectedSubMaps = " + str(collectedSubMaps) )

    if not provTools.checkAttValsPerRule( collectedSubMaps ) : # sanity check
      sys.exit( "**** FATAL ERROR ****\nAttribute mappings across the subgoals in a rule do not match up.\nsubgoal value maps:\n" + str(collectedSubMaps) )

    else :
      for subMap in collectedSubMaps :
        subName       = subMap[0]

        # handle isNeg
        isNeg_str     = subMap[1]
        if isNeg_str == "notin" :
          isNeg = True
        else :
          isNeg = False

        subAttMapping = subMap[2]
        firing  = provTools.getFiring( subAttMapping )

        #if subName == "missing_log" :
        #  sys.exit( "BREAKPOINT " + __name__+ " : subName = " + subName + ", isNeg = " + str(isNeg) )

        self.spawnNode( subName, isNeg, firing )

  ################
  #  SPAWN NODE  #
  ################
  def spawnNode( self, subName, isNeg, firing ) :

    if DEBUG :
      print "++++++++++++++++++++++++++++++++++++++++++"
      print "        CREATING SPAWN NODE"
      print "self.name     = " + str( self.name )
      print "self.treeType = " + str( self.treeType )
      print "self.record   = " + str( self.record )
      print "subName       = " + str( subName )
      print "isNeg         = " + str( isNeg )
      print "firing        = " + str( firing )
      print "++++++++++++++++++++++++++++++++++++++++++"

    self.descendants.append( DerivTree.DerivTree( subName, "goal", isNeg, firing, self.results, self.cursor ) )


#########
#  EOF  #
#########
