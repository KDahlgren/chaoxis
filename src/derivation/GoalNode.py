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
  descendants     = []
  possibleFirings = []


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record, results, cursor ) :

    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "goal", name, isNeg, record, results, cursor )

    # need to make sure descendants list is empty or else
    # pyDot creates WAAAAAAAAY too many edges for some reason??? <.<
    self.descendants = []


    if DEBUG :
      print "<><><><><><><><><><><><><><><><><><><>"
      print "CREATING GOAL FOR : "
      print "  self.name   = " + str(self.name )
      print "  self.isNeg  = " + str( self.isNeg )
      print "  self.record = " + str( self.record )
      print "<><><><><><><><><><><><><><><><><><><>"

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # CASE 0 : goal specifies a fact
    # launch fact descendants
    if tools.isFact( self.name, self.cursor ) :
      self.setDescendants( "isFact" )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # CASE 1 : goal is negative
    elif self.isNeg :
      pass

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # CASE 2 : goal does not specify a fact
    elif not tools.isFact( self.name, self.cursor ) :
      self.setDescendants( "notFact" )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # CASE 3 : idk
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : goal is a fact and is not a fact. Wot??")


    if DEBUG :
      print "---------------------------------------"
      print "IN GOAL NODE " + str(self.name) + ", PRINTING " + str(len(self.descendants)) + " DESCENDANTS"
      for d in self.descendants :
        print "d.root.treeType = " + str(d.root.treeType)
        print "d.root.name     = " + str(d.root.name)
        print "d.root.isNeg    = " + str(d.root.isNeg)
        print "d.root.record   = " + str(d.root.record)
      print "---------------------------------------"


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

  ##################
  #  FMLA DISPLAY  #
  ##################
  def fmlaDisplay( self ) :
    return str( self )

  #############
  #  DISPLAY  #
  #############
  # the string representation of a GoalNode
  def display( self ) :
    myStr = None

    if self.isNeg :
      negStr = "_NOT_ "
      myStr =  negStr + "," + self.name + "(" + str(self.record) + ")"

    else :
      myStr = self.name + "(" + str(self.record) + ")"

    return str( myStr )


  #####################
  #  SET DESCENDANTS  #
  #####################
  # goal nodes may have more than one descendant in the case of wildcards
  # and when multiple firing records exist for the particular.
  def setDescendants( self, category ) :

    if DEBUG :
      print "self.name                              = " + self.name
      print "self.isNeg                             = " + str( self.isNeg )
      print "self.record                            = " + str( self.record )
      print "tools.isFact( self.name, self.cursor ) = " + str( tools.isFact( self.name, self.cursor ) )

    # ==================================================== #
    if category == "isFact" :

      # handle wildcards in fact goals
      if "__WILDCARD__" in self.record :

        # grab all partially matching records
        allPartialMatches = provTools.getPartialMatches( self.name, self.record, self.results )

        for rec in allPartialMatches :
          self.spawnFact( rec )

      else :
        self.spawnFact( self.record )

    # ==================================================== #
    elif category == "notFact" :
      # get all (origRuleID, provRuleID) pairs for this rule name.
      allPairs = self.getIDPairs( self.name )

      # get all candidate rule attribute maps to values from record.
      # returns dictionary connecting original rule ids with associated att mappings (also dictionaries)
      candMaps = self.getAllCandidateMaps( self.getIDSubset( allPairs, "orig" ), self.record )

      # iterate over prov ids to obtain a set of valid records per provenance rule which could have triggered 
      # the appearance of self.record in the name relation.
      # store valid record sets per prov id in a dictionary keyed by prov ids.
      validFirings = self.getFirings( allPairs, candMaps )

      # spawn a rule node for all valid firing records per provenance rule
      for provID in validFirings :
        firingRecs = validFirings[ provID ]

        for rec in firingRecs :
          self.spawnRule( provID, rec )

    # ==================================================== #
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized goal category '" + str(category) + "'" )


  #################
  #  GET FIRINGS  #
  #################
  # allPairs := an array of tuples connecting original rids with corrseponding provenance rule ids
  # candMaps := a dictionary connecting original rids with dictionaries mapping original goal atts to record values
  def getFirings( self, allPairs, candMaps ) :

    validFirings = {} # dictionary mapping individual prov ids to individual arrays of valid firing records.

    for p in allPairs :
      currorid = p[0]
      currprid = p[1]

      # get provenance rule name
      self.cursor.execute( "SELECT goalName FROM Rule WHERE rid='" + currprid + "'" )
      provName = self.cursor.fetchone()
      provName = tools.toAscii_str( provName )

      # get goal attList per prov rule id
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid='" + currprid + "'" )
      pschema = self.cursor.fetchall()
      pschema = tools.toAscii_multiList( pschema )

      # generate list of schema atts
      pschema_list = []
      for arr in pschema :
        pschema_list.append( arr[1] )

      # get a partial map of goal attributes to record values
      currOrigAttMap = candMaps[ currorid ]
      currProvAttMap = {}
      for attArr in pschema :
        att = attArr[1]

        # case attribute has a hard binding in the input record,
        # then provenance attribute has the same binding.
        if att in currOrigAttMap.keys() :
          currProvAttMap[ att ] = currOrigAttMap[ att ]

        # case attribute is a wildcard, then provenance binding is None.
        elif currOrigAttMap[ att ] == "__WILDCARD__" :
          currProvAttMap[ att ] = None

        # case attribute does not appeat in the original rule schema,
        # then the provenance binding is None.
        else :
          currProvAttMap[ att ] = None

      # iterate over records in provenance relation and save the records which agree with the partial mapping
      provRecs     = self.results[ provName ]
      validRecList = []
      for rec in provRecs :
        if self.checkAgreement( pschema_list, currProvAttMap, rec ) :
          validRecList.append( rec )

      validFirings[ currprid ] = validRecList

    return validFirings


  ################
  #  SPAWN FACT  #
  ################
  def spawnFact( self, seedRecord ) :
    self.descendants.append( DerivTree.DerivTree( self.name, None, "fact", self.isNeg, seedRecord, self.results, self.cursor ) )


  ################
  #  SPAWN RULE  #
  ################
  def spawnRule( self, rid, seedRecord ) :
    self.descendants.append( DerivTree.DerivTree( self.name, rid, "rule", False, seedRecord, self.results, self.cursor ) )


  #####################
  #  CHECK AGREEMENT  #
  #####################
  # a record in the prov version of the original rule may only be a valid
  # potential firing if the contents of the prov record at all the relevant contents
  # of the input record derived from the original rule relation.
  def checkAgreement( self, schema, attMap, record ) :

    # iterate over attributes in the prov schema
    for i in range( 0, len(schema) ) :
      currAtt  = schema[ i ]
      currItem = record[ i ]

      # if the contents of the record doesn not match the map assignment derived from 
      # the input record from the original rule table, then the provenance record under 
      # consideration is invalid. Semantically, the record could not have triggered the 
      # appearance of the input record in the original rule table.
      # Additionally, the mapping for the attribute must be non-empty. Otherwise,
      # the record may still represent a valid trigger because that attribute does not
      # appear as an attribute in the original rule and, therefore, possesses no hard 
      # binding according to the input record.
      if (not currItem == attMap[ currAtt ]) and (not attMap[ currAtt ] == None) :
        return False

    return True


  ##################
  #  GET ID PAIRS  #
  ##################
  # match the ids of oiginal rules to the ids of the associated derived provenance rules.
  # there exists only one prov rule per original rule.
  def getIDPairs( self, rname ) :

    # ---------------------------------------------------------- #
    #                      ORIG RULE DATA                        #
    # ---------------------------------------------------------- #
    # get all original rule ids associated with the name
    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + rname + "'" )
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
    # get all provenance rule ids associated with the rname
    # first, get all rule id, rule name pairs
    self.cursor.execute( "SELECT rid,goalName FROM Rule" )
    idNamePairs = self.cursor.fetchall()
    idNamePairs = tools.toAscii_multiList( idNamePairs )

    # next, collect the rids of goalnames starting with rname+"_prov"
    provIDs = []
    for idName in idNamePairs :
      currID   = idName[0]
      currName = idName[1]
      if currName.startswith( rname + "_prov" ) :
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


  ###################
  #  GET ID SUBSET  #
  ###################
  # return either all the original ids or all the provenance ids
  def getIDSubset( self, allPairs, idType ) :

    idList = []

    for p in allPairs :
      orid = p[0]
      prid = p[1]

      if idType == "orig" :
        idList.append( orid )

      elif idType == "prov" :
        idList.append( prid )

      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: unrecognized id subset type (only 'orig' and 'prov' currently supported) : " + str(idType) )

    return idList


  ############################
  #  GET ALL CANDIDATE MAPS  #
  ############################
  # map the attributes for the original rule to values in record.
  # works because all rule ids (orig and prov) are unique
  def getAllCandidateMaps( self, idList, record ) :

    candidateOrigRuleMaps = {}

    currMap = {}
    for i in idList :

      # get goal attList
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid='" + i + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      # map attnames to values in record
      for j in range(0,len(attList)) :
        att     = attList[j]
        attName = att[1]

        # case of adding the attribute to currMap for the first time
        if not attName in currMap.keys() :
          currMap[ attName ] = record[j]

        # case of considering attribute for insertion into currMap after the first time
        # the corresponding values in the record should be identical, or else the datalog
        # evaluator is screwed up.
        elif not currMap[ attName ] == record[j] :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : multiple record values exist for the same attribute in this rule: \nattName = " + attName + " --> " + currMap[ attName ] + " and\nattName = " + attName + " --> " + record[j] )

      # save the map
      if j == len(attList) - 1 :
        candidateOrigRuleMaps[ i ] = currMap
        currMap = {}

    return candidateOrigRuleMaps


#########
#  EOF  #
#########
