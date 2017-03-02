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
  firing      = None
  rid         = None

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, rid, record, results, cursor ) :
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, db cursor
    Node.__init__( self, "rule", name, False, record, results, cursor )

    self.firing = record
    self.rid    = rid

    if DEBUG :
      print "*************************************"
      print "    RULE NODE INIT DATA"
      print "  name   = " + str( name )
      print "  record = " + str( record )
      print "*************************************"

    # launch descendants
    self.descendants = [] # needed or else pyDot creates WAAAAAAAAY too many edges for some reason??? <.<
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
    return "rule-> "+ self.name + "(" + str(self.record) + ")"


  #####################
  #  SET DESCENDANTS  #
  #####################
  # rule nodes have one or more descendants.
  # all descendants are goal nodes.
  def setDescendants( self ) :

    # assumes self.rid is the provenance rid for this rule
    pgoalAttMap = self.getProvGoalAttMap()

    # get the info for all the subgoals of this rule
    subgoalInfo = self.getSubgoalInfo()

    # per subgoal, map subgoal attributes to values from the firing record.
    collectedSubMaps = []
    for sub in subgoalInfo :
      subName = sub[0]
      isNeg   = sub[1][0]
      attList = sub[2]

      # get sub att map
      subAttMap = self.setSubAttMap( attList, pgoalAttMap )
      collectedSubMaps.append( (subName, isNeg, subAttMap) )

    # iterate over populated subgoal maps
    for subMap in collectedSubMaps :
      subName       = subMap[0]
      subAttMapping = subMap[2]

      # handle isNeg for this subgoal
      isNeg_str     = subMap[1]
      if isNeg_str == "notin" :
        isNeg = True
      else :
        isNeg = False

      # spawn the descendant goal node
      self.spawnNode( subName, isNeg, self.firing )


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

    self.descendants.append( DerivTree.DerivTree( subName, None, "goal", isNeg, firing, self.results, self.cursor ) )


  ######################
  #  GET SUBGOAL INFO  #
  ######################
  # grab the set of subgoals for this rule
  # note the subgoal and lists for both original and provenance rules are identical.
  def getSubgoalInfo( self ) :
    subgoalInfo = []
  
    # grab all subgoals for the prov rule
    self.cursor.execute( "SELECT subgoalName,sid FROM Subgoals WHERE rid=='" + self.rid + "'" )
    subInfo = self.cursor.fetchall()
    subInfo = tools.toAscii_multiList( subInfo )
  
    # grab all the atts per subgoal
    # plus isNeg value.
    for sub in subInfo :
      name = sub[0]
      sid  = sub[1]
  
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + self.rid + "' AND sid=='" + sid + "'" )
      attInfo = self.cursor.fetchall()
      attInfo = tools.toAscii_multiList( attInfo )
  
      self.cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid=='" + self.rid + "' AND sid=='" + sid + "'" )
      negInfo = self.cursor.fetchall()
      negInfo = tools.toAscii_list( negInfo )
  
      if len( negInfo ) >= 1 :
        if not negInfo[0] == "notin" :
          sys.exit( "**** FATAL ERROR ****\nUnrecognized prefix argument to rule subgoal in " + str(cleanNegInfo) + "\nAborting..." )
      else :
        negInfo.append( "" ) # no prefix means subgoal is positive
  
      # ---------------------------------- #
      # sanity checks
      if len( attInfo ) < 1 :
        sys.exit( "**** FATAL ERROR ****\nNo attributes for subgoal " + name + "\nAborting..." )
  
      if len( negInfo ) > 1 :
        print "**** WARNING ****:\nMore than one additional prefix argument exists for the subgoal of a rule in the input program. The current version of pyLDFI only supports one optional prefix argument per subgoal, notin. Proceeding by taking the first additional argument by default."
      # ---------------------------------- #
  
      # clean up att list
      cleanList = []
      for att in attInfo :
        attID   = att[0]
        attName = att[1]
        cleanList.append( attName )
  
      # define subgoal info tuple
      newTup = ( name, negInfo, cleanList )
      subgoalInfo.append( newTup )

    return subgoalInfo


  ###########################
  #  GET PROV GOAL ATT MAP  #
  ###########################
  def getProvGoalAttMap( self ) :

    # get goal att list for the prov rule
    self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid='" + self.rid + "'" )
    attList = self.cursor.fetchall()
    attList = tools.toAscii_multiList( attList )
    attList = [ attInfo[1] for attInfo in attList ] # get att strings only

    attMap = {}
    for i in range(0,len(attList)) :
      attMap[ attList[ i ] ] = self.record[ i ]

    return attMap


  #####################
  #  SET SUB ATT MAP  #
  #####################
  def setSubAttMap( self, subAttList, attMap ) :

    subAttMap = {}

    for att in subAttList :
      if (att in attMap.keys()) :
        subAttMap[ att ] = attMap[ att ]
      elif att == "_" :
        pass
      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : subgoal attribute '" + att + "' does not exist in the provenance att map '" + str(attMap) + "'"  )

    return subAttMap


#########
#  EOF  #
#########
