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
  descendants   = []
  prid          = None
  provAttMap    = None
  triggerRecord = None

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, prid, provAttMap, record, results, cursor ) :

    # ///////////////////////////////////////////////////////// #
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, db cursor
    Node.__init__( self, "rule", name, False, record, results, cursor )

    # ///////////////////////////////////////////////////////// #
    # collect parent goal data
    self.prid          = prid
    self.provAttMap    = provAttMap
    self.triggerRecord = record

    # ///////////////////////////////////////////////////////// #
    # fill in provenance attribute mapping Nones with data from 
    # the trigger record.
    fullProvMap = self.getFullMap()

    #tools.bp( __name__, inspect.stack()[0][3], "fullProvMap = " + str(fullProvMap) )

    # ///////////////////////////////////////////////////////// #
    # get all subgoal info:
    #   subgoal names and subgoal attribute mappings, given 
    #   the fullProvMap
    subgoalInfo = self.getSubgoalInfo( fullProvMap )

    # ///////////////////////////////////////////////////////// #
    # extract subgoal trigger records based on the subgoal 
    # att maps
    subgoalSeedRecords = self.getSubgoalSeedRecords( subgoalInfo )

    # ///////////////////////////////////////////////////////// #
    # launch descendants
    self.descendants = [] # needed or else pyDot creates WAAAAAAAAY too many edges for some reason??? <.<
    self.setDescendants( subgoalSeedRecords )

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


  ##################
  #  GET FULL MAP  #
  ##################
  # return a version of the provAttMap with all None's replaced with 
  # appropriate data from the trigger record
  def getFullMap( self ) :

    # sanity check
    # the arity of the provenance schema must equal
    # the arity of the trigger record.
    if not len( self.provAttMap ) == len( self.triggerRecord ) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : the arity of the provenance schema does not equal the arity of the provenance trigger record...You got serious probs =[\nself.provAttMap = " + str(self.provAttMap) + "\nself.triggerRecord = " + str(self.triggerRecord) )

    fullProvAttMap = []
    for i in range(0,len(self.provAttMap)) :
      attValPair = self.provAttMap[ i ]
      att = attValPair[0]
      val = attValPair[1]
      recval = self.triggerRecord[ i ]

      if val == None :
        fullProvAttMap.append( [ att, recval ] )
      elif val == recval :
        fullProvAttMap.append( attValPair )
      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : the attribute mappings for the provenance rule do not agree with the data in the provenance trigger rule...You got serious probs, mate =[\nself.provAttMap = " + str(self.provAttMap) + "\nself.triggerRecord = " + str(self.triggerRecord) )
      
    return fullProvAttMap


  ######################
  #  GET SUBGOAL INFO  #
  ######################
  # return an array of binary arrays connecting each subgoal name
  # with a corresponding array of binary arrays connecting 
  # the subgoal attributes with appropriate values, as specified 
  # by the fullProvMap.
  def getSubgoalInfo( self, fullProvMap ) :
    # ------------------------------------------------------------- #
    # Transform the provAttMap into a dictionary for convenience.
    fullProvDict = {}
    for arr in fullProvMap :
      att = arr[0]
      val = arr[1]

      # sanity check
      if att in fullProvDict.keys() and not val == fullProvDict[ att ] :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : multiple data values exist for the same attribute.\nattribute = " + att + "\nval = " + val + " and ogattDict[ att ] = " + fullProvDict[ att ] )
      else : # add to dictionary
        fullProvDict[ att ] = val
    # ------------------------------------------------------------- #

    subgoalInfo = []

    # get the list of subgoals
    self.cursor.execute( "SELECT sid,subgoalName FROM Subgoals WHERE rid=='" + self.prid + "'" )
    subIDNameList = self.cursor.fetchall()
    subIDNameList = tools.toAscii_multiList( subIDNameList )

    # for each sid, grab the subgoal attribute list and the isNeg
    for idNamePair in subIDNameList :
      sid     = idNamePair[0]
      subname = idNamePair[1]

      # get the attribute list for this subgoal
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + self.prid + "' AND sid=='" + sid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )
      attList = [ idNamePair[1] for idNamePair in attList ]

      # get the isNeg information
      self.cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid=='" + self.prid + "' AND sid=='" + sid + "'" )
      isNeg = self.cursor.fetchone()
      if isNeg :
        isNeg = tools.toAscii_str( isNeg )
      else :
        isNeg = ""

      # ///////////////////////////////////////////////////////// #
      # Map each attribute to a value based on the mappings from 
      # the full provAttMap.
      thisSubAttMap = []
      for att in attList :
        #if att == "__WILDCARD__" :
        if att == "_" :
          thisSubAttMap.append( [ att, None ] )
        elif att in fullProvDict.keys() :
          thisSubAttMap.append( [ att, fullProvDict[ att ] ] )
        else :
          thisSubAttMap.append( [ att, None ] )

      subgoalInfo.append( [ subname, isNeg, thisSubAttMap ] )
      # ///////////////////////////////////////////////////////// #

    return subgoalInfo


  ##############################
  #  GET SUBGOAL SEED RECORDS  #
  ##############################
  # return subgoal trigger records, as suggested by the subgoal att mappings
  def getSubgoalSeedRecords( self, subgoalInfo ) :

    subgoalSeedRecords = []

    for subgoal in subgoalInfo :
      subname = subgoal[0]
      isNeg   = subgoal[1]
      attMap  = subgoal[2]

      triggerRec = []
      for attPair in attMap :
        attName = attPair[0]
        val     = attPair[1]

        if attName == "_" :
          triggerRec.append( "_" )
        else :
          triggerRec.append( val )

      subgoalSeedRecords.append( [ subname, isNeg, triggerRec ] )

    return subgoalSeedRecords


  #####################
  #  SET DESCENDANTS  #
  #####################
  # rule nodes have one or more descendants.
  # all descendants are goal nodes.
  def setDescendants( self, subgoalSeedRecords ) :

    # iterate over subgoals
    for subgoal in subgoalSeedRecords :
      subName    = subgoal[0]
      seedRecord = subgoal[2]

      # handle isNeg for this subgoal
      isNeg_str = subgoal[1]
      if isNeg_str == "" :
        isNeg = False
      else :
        isNeg = True

      # spawn the descendant goal node
      self.spawnNode( subName, isNeg, seedRecord )


  ################
  #  SPAWN NODE  #
  ################
  def spawnNode( self, subName, isNeg, seedRecord ) :
    self.descendants.append( DerivTree.DerivTree( subName, None, "goal", isNeg, None, seedRecord, self.results, self.cursor ) )


#########
#  EOF  #
#########
