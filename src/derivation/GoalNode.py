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

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, seedRecord, results, cursor ) :

    # ///////////////////////////////////////////////////////// #
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "goal", name, isNeg, seedRecord, results, cursor )

    # ***************************************************************** #
    # ***************************************************************** #
    #                      HANDLE CLOCK GOALS
    #
    if self.name == "clock" :
      triggerRecordList = self.getClockTriggerRecordList()

    else :
      # ///////////////////////////////////////////////////////// #
      # get all id pairs ( original rid, provenance rid ) 
      # for this name
      allIDPairs = self.getAllIDPairs()

      # ///////////////////////////////////////////////////////// #
      # for each original rid, map original goal atts to values
      # from the seed record.
      oridList = [ aPair[0] for aPair in allIDPairs ]
      ogattMaps = self.getGoalAttMaps( oridList )

      if self.name == "a_table" :
        print "self.name = " + str( self.name )
        print "ogattMaps = " + str( ogattMaps )

      # ///////////////////////////////////////////////////////// #
      # for each provenance rule id, use the corresponding orid map
      # for goal atts to seed record values to map provenance rule 
      # goal atts to seed record values or None.
      # Map WILDCARDs to None.
      pgattMaps = self.mergeMaps( allIDPairs, ogattMaps )

      # ///////////////////////////////////////////////////////// #
      # for each prid, grabs the full set of records from 
      # the provenance relation which may have triggered 
      # the appearance of the seed record in the original 
      # rule relation.
      triggerRecordList = self.getAllTriggerRecords( pgattMaps )

    # ***************************************************************** #
    # ***************************************************************** #

    # ///////////////////////////////////////////////////////// #
    # set the descendants of this goal node.
    #
    # Need to make sure descendants list is empty or else
    # pyDot creates WAAAAAAAAY too many edges for some reason??? <.<
    self.descendants = []

    # TODO: support negative provenance ...
    if self.isNeg :
      pass
    else :
      self.setDescendants( triggerRecordList )


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
    if self.isNeg :
      negStr = "_NOT_ "
      myStr =  negStr + "," + self.name + "(" + str(self.record) + ")"
    else :
      myStr = self.name + "(" + str(self.record) + ")"
    return str( myStr )


  ###################
  #  GET CLOCK MAP  #
  ###################
  def getClockTriggerRecordList( self ) :

    # sanity check
    # all clock records adhere to the same arity-4 schema: src, dest, SndTime, DelivTime
    if not len(self.record) == 4 :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : clock record does not adhere to clock schema(src,dest,SndTime,DelivTime) : \nself.record = " + str(self.record) )

    # get clock record data
    src       = self.record[0]
    dest      = self.record[1]
    sndTime   = self.record[2]
    delivTime = self.record[3]

    # get all matching (or partially matching, in the case of '_') clock records
    # optimistic by default
    qSRC       = "src=='" + src + "'"
    qDEST      = " AND dest=='" + dest + "'"
    qSNDTIME   = " AND sndTime==" + sndTime + ""
    qDELIVTIME = " AND delivTime==" + delivTime + ""

    # erase query components as necessary
    # EXISTING BUG TODO : does not work if _ in src --> need to handle ANDs more intelligently
    if "_" in src :
      qSRC = ""
    if "_" in dest :
      qDEST = ""
    if "_" in sndTime :
      qSNDTIME = ""
    if "_" in delivTime :
      qDELIVTIME = ""

    # set query
    query = "SELECT src,dest,sndTime,delivTime FROM Clock WHERE " + qSRC + qDEST + qSNDTIME + qDELIVTIME

    if DEBUG :
      print "query = " + str(query)

    # execute query
    self.cursor.execute( query )
    triggerRecordList = self.cursor.fetchall()
    triggerRecordList = tools.toAscii_multiList( triggerRecordList )

    return triggerRecordList


  ######################
  #  GET ALL ID PAIRS  #
  ######################
  # match the ids of oiginal rules to the ids of the associated derived provenance rules.
  # there exists only one prov rule per original rule.
  # return a list of binary lists connecting original rule ids and 
  # corresponding provenance rule ids.
  def getAllIDPairs( self ) :

    # ---------------------------------------------------------- #
    #                      ORIG RULE DATA                        #
    # ---------------------------------------------------------- #
    # get all original rule ids associated with the name
    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + self.name + "'" )
    origIDs = self.cursor.fetchall()
    origIDs = tools.toAscii_multiList( origIDs )

    # get the complete attList and subgoalList associated with each original rule
    # store as arrays in an array [ rid, [attList], [subgoalList] ]
    origInfo = []
    for orid in origIDs :
      orid = orid[0] # origIDs is a list of singular lists

      # get attList
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid='" + orid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      # get subgoalList
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid='" + orid + "'" )
      subgoalList = self.cursor.fetchall()
      subgoalList = tools.toAscii_multiList( subgoalList )

      origInfo.append( [ orid, attList, subgoalList ] )

    # ---------------------------------------------------------- #
    #                      PROV RULE DATA                        #
    # ---------------------------------------------------------- #
    # get all provenance rule ids associated with the name
    # first, get all rule id, rule name pairs
    self.cursor.execute( "SELECT rid,goalName FROM Rule" )
    idNamePairs = self.cursor.fetchall()
    idNamePairs = tools.toAscii_multiList( idNamePairs )

    # next, collect the rids of goalnames starting with self.name+"_prov"
    provIDs = []
    for idName in idNamePairs :
      currID   = idName[0]
      currName = idName[1]
      if currName.startswith( self.name + "_prov" ) :
        provIDs.append( currID )

    # get the complete attList and subgoalList associated with each original rule
    # store as arrays in an array [ rid, [attList], [subgoalList] ]
    provInfo = []
    for prid in provIDs :
      # get attList
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid='" + prid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      # get subgoalList
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid='" + prid + "'" )
      subgoalList = self.cursor.fetchall()
      subgoalList = tools.toAscii_multiList( subgoalList )

      provInfo.append( [ prid, attList, subgoalList ] )

    # ---------------------------------------------------------- #
    #                         MATCH                              #
    # ---------------------------------------------------------- #
    # match original rids with provenance rids by matching
    # attLists and subgoals.
    idPairs = []
    for origIDInfo in origInfo :
      orid     = origIDInfo[0]
      oAttList = origIDInfo[1]
      oSubList = origIDInfo[2]

      for provIDInfo in provInfo :
        prid     = provIDInfo[0]
        pAttList = provIDInfo[1]
        pSubList = provIDInfo[2]

        if self.checkListEquality( oAttList, pAttList ) and self.checkListEquality( oSubList, pSubList ) :
          idPairs.append( [ orid, prid ] ) # save pair

    return idPairs


  #########################
  #  CHECK LIST EQUALITY  #
  #########################
  # check list equality
  # 1. list lengths must be equal
  # 2. all elements in each list must appear in the other list
  def checkListEquality( self, list1, list2 ) :

    # check length equality
    if len( list1 ) == len( list2 ) :
      pass
    else :
      return False

    # check contents equality
    for item in list1 :
      if not item in list2 :
        return False
  
    return True


  #######################
  #  GET GOAL ATT MAPS  #
  #######################
  # return an ordered array of binary arrays connecting goal 
  # attributes from the original rule the values from the seed record.
  def getGoalAttMaps( self, oridList ) :
    ogattMap = []

    # get the ordered list of goal attributes for each orid
    oridAttLists = []
    for orid in oridList :
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + orid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )
      attList = [ aPair[1] for aPair in attList ]

      oridAttLists.append( [ orid, attList ] )

    # for each orid:attList, connect atts to vals from seed record
    for oridInfo in oridAttLists :
      thisorid    = oridInfo[0]
      thisattList = oridInfo[1]

      # sanity check
      # the number of goal atts in the original rule must match
      # the number of values in the seed record.
      if (len( thisattList ) < len( self.record )) or (len( thisattList ) > len( self.record )) :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : number of attributes in goal attribute list for " + self.name + " does not match the number of values in the seed record:\nattribute list = " + str(thisattList) + "\nrecord = " + str(self.record) )

      # map atts to values from the seed record
      thisAttValList = []
      for i in range(0,len(thisattList)) :
        att = thisattList[ i ]
        val = self.record[ i ]
        thisAttValList.append( [ att, val ] )

      ogattMap.append( [ thisorid, thisAttValList ] )

    return ogattMap


  ################
  #  MERGE MAPS  #
  ################
  # for each provenance rule id, use the corresponding orid map
  # for goal atts to seed record values to map provenance rule 
  # goal atts to seed record values or None.
  # Map WILDCARDs to None.
  def mergeMaps( self, allIDPairs, ogattMaps ) :
    pgattMaps = []

    # get list of all prids
    pridList = [ aPair[1] for aPair in allIDPairs ]

    for prid in pridList :

      # get the goal att list for this provenance rule
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + prid + "'" )
      pgattList = self.cursor.fetchall()
      pgattList = tools.toAscii_multiList( pgattList )
      pgattList = [ arr[1] for arr in pgattList ]

      # get corresponding original rule id
      orid = self.getORID( prid, allIDPairs )

      # ///////////////////////////////////////////////////////// #
      # get map of goal atts for the original rule 
      # to seed record values.
      # ------------------------------------------------------------- #
      # Transform into dictionary for convenience
      thisogattMap = self.getOGattMap( orid, ogattMaps )

      ogattDict = {}
      for arr in thisogattMap :
        att = arr[0]
        val = arr[1]

        # sanity check
        if att in ogattDict.keys() and not val == ogattDict[ att ] :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : multiple data values exist for the same attribute.\nattribute = " + att + "\nval = " + val + " and ogattDict[ att ] = " + ogattDict[ att ] )
        else : # add to dictionary
          ogattDict[ att ] = val
      # ------------------------------------------------------------- #

      # map provenance goal atts to values from the seed record based on 
      # the attribute mappings in the original rule.
      # unspecified atts are mapped to None.
      # WILDCARDs are mapped to None.
      pattMapping = []
      for patt in pgattList :
        #if patt == "__WILDCARD__" :
        if patt == "_" :
          pattMapping.append( [ patt, None ] )
        elif patt in ogattDict.keys() :
          pattMapping.append( [ patt, ogattDict[ patt ] ] )
        else :
          pattMapping.append( [ patt, None ] )

      pgattMaps.append( [ prid, pattMapping ] )
      # ///////////////////////////////////////////////////////// #

    return pgattMaps


  ################################################
  #  GET O(riginal Rule) G(oal) ATT(ribute) MAP  #
  ################################################
  def getOGattMap( self, orid, ogattMaps ) :

    for aMap in ogattMaps :
      currorid = aMap[0]
      currmap  = aMap[1]

      if orid == currorid :
        return currmap

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : the original rule id " + orid + " has no goal attribute mapping in ogattMaps = " + str(ogattMaps) )


  ##############
  #  GET ORID  #
  ##############
  def getORID( self, prid, allIDPairs ) :

    for aPair in allIDPairs :
      currorid = aPair[0]
      currprid = aPair[1]

      if prid == currprid :
        return currorid

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : provenance id " + prid + " has no corresponding original rule id. You got major probs... =["  )


  #############################
  #  GET ALL TRIGGER RECORDS  #
  #############################
  # return list of binary lists connecting each prid
  # with a list of records (stored as lists) from the 
  # provenance record which may have triggered the
  # appearance of the seed record in the original rule
  # relation.
  def getAllTriggerRecords( self, pgattMaps ) :

    pTrigRecs = []

    for attMap in pgattMaps :
      prid    = attMap[0]
      mapping = attMap [1]

      # get full relation name
      self.cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + prid + "'" )
      pname = self.cursor.fetchone() # goalName should be unique per provenance rule
      pname = tools.toAscii_str( pname )

      # get full results table
      resultsTable = self.results[ pname ]

      # get list of valid records which agree with the provenance rule 
      # goal attribute mapping
      # correctness relies upon ordered nature of the mappings.
      validRecList = []
      for rec in resultsTable :
        if self.checkAgreement( mapping, rec ) :
          validRecList.append( rec )

      pTrigRecs.append( [ prid, mapping, validRecList ] )

    return pTrigRecs


  #####################
  #  CHECK AGREEMENT  #
  #####################
  def checkAgreement( self, mapping, rec ) :

    # sanity check
    if not len(mapping) == len( rec ) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : arity of provenance schema not equal to arity of provenance records:\nmapping = " + str(mapping) + "\nrec = " + str(rec) + "\nYou got probs. =[ Aborting..." )

    for i in range(0,len(mapping)) :
      attValPair = mapping[i]
      att        = attValPair[0]
      val        = attValPair[1]
      recval     = rec[i]

      if val == None :
        pass
      elif val == recval :
        pass
      else :
        return False

    return True


  #####################
  #  SET DESCENDANTS  #
  #####################
  # goal nodes may have more than one descendant in the case of wildcards
  # and when multiple firing records exist for the particular.
  def setDescendants( self, triggerRecordList ) :

    # ==================================================== #
    # ==================================================== #
    #   CASE goal is a fact
    if tools.isFact( self.name, self.cursor ) :

      # ************************************************* #
      #                HANDLE CLOCK FACTS                 #
      #
      # triggerRecordList := list of trigger records 
      if self.name == "clock" :
        # spawn a fact for each trigger record
        for rec in triggerRecordList :
          self.spawnFact( rec )

      # ************************************************* #
      #                HANDLE OTHER FACTS                 #
      #
      # triggerRecordList := list of trinary lists 
      #     containing the prid, the prov att map, and
      #     the list of trigger records.
      else :
        # get complete list of trigger records
        trigList = []
        for trigRec in triggerRecordList :
          trigList.extend( trigRec[2] )

        #tools.bp( __name__, inspect.stack()[0][3], "trigList = " + str(trigList) )

        # spawn a fact for each trigger record
        for rec in trigList :
          self.spawnFact( rec )

    # ==================================================== #
    #   CASE goal is a rule
    else :
      for trigRec in triggerRecordList :
        provID     = trigRec[0]
        provAttMap = trigRec[1]
        recList    = trigRec[2]

        # spawn a rule for each valid record
        for rec in recList :
          self.spawnRule( provID, provAttMap, rec )

    # ==================================================== #
    # ==================================================== #

  ################
  #  SPAWN FACT  #
  ################
  def spawnFact( self, trigRec ) :
    self.descendants.append( DerivTree.DerivTree( self.name, None, "fact", self.isNeg, None, trigRec, self.results, self.cursor ) )


  ################
  #  SPAWN RULE  #
  ################
  def spawnRule( self, rid, provAttMap, seedRecord ) :
    self.descendants.append( DerivTree.DerivTree( self.name, rid, "rule", False, provAttMap, seedRecord, self.results, self.cursor ) )


#########
#  EOF  #
#########
