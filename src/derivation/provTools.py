#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, pydot, sys

packagePath2  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath2 )
from utils import tools

# **************************************** #

DEBUG = True
C4_RESULTS_PATH = os.path.abspath( __file__ + "/../../../save_data/c4Output/c4dump.txt" )


#################
#  CREATE NODE  #
#################
def createNode( nodeToAdd ) :

  if nodeToAdd.treeType == "goal" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='oval' )

  elif nodeToAdd.treeType == "rule" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='box' )

  elif nodeToAdd.treeType == "fact" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='cylinder' )

  else :
    sys.exit( "********************\n********************\nFATAL ERROR in file " + __name__ + " in function " + inspect.stack()[0][3] + " :\nUnrecognized treeType" + str( nodeToAdd.treeType ) )

  return thisNode


################
#  GET FIRING  #
################
# subAttMapping := a list of (att, value) tuples
# return list of values (respecting original ordering)
def getFiring( subAttMapping ) :

  valList = []

  for mapping in subAttMapping :
    val = mapping[1]
    valList.append( val )

  return valList


#############################
#  CHECK ATT VALS PER RULE  #
#############################
def checkAttValsPerRule( collectedSubMaps ) :

  for subMap1 in collectedSubMaps :
    for subMap2 in collectedSubMaps :
      valMap1 = subMap1[2]
      valMap2 = subMap2[2]
      for map1 in valMap1 :
        for map2 in valMap2 :
          att1 = map1[0]
          att2 = map2[0]
          val1 = map1[1]
          val2 = map2[1]
          if att1 == att2 :
            if not val1 == val2 :
              return False

  return True


#####################
#  GET SUB ATT MAP  #
#####################
# map the attributes of subgoals to values from the goal mapping
# goalAttMap contains an incomplete mapping of atts to values based on the provenance att and the raw record.  Need to find the set of tuples from the subgoal relation (not the prov version) which completely or partially match the bindings.
def getSubAttMap( subName, subAttList, goalAttMap ) :

  if DEBUG :
    print  "subName    = " + str( subName )
    print  "subAttList = " + str( subAttList )
    print  "goalAttMap = " + str( goalAttMap )


  subAttMap = []

  for sattName in subAttList :
    if sattName == "_" :
      subAttMap.append( ( sattName, "__WILDCARD__" ) )

    else :
      val = getAttVal( sattName, goalAttMap )
      if val :
        subAttMap.append( (sattName, val) )
      else :
        subAttMap.append( (sattName, None) )

  return subAttMap


#################
#  GET ATT VAL  #
#################
def getAttVal( att, goalAttMap ) :
  val = None
  for gTup in goalAttMap :
    gattName = gTup[0]
    gattVal  = gTup[1]
    if att == gattName :
      val = gattVal

  return val


######################
#  GET GOAL ATT MAP  #
######################
# map the goal attributes from the prov rule to values from the record.
# assume validity of left-to-right ordering
# returns an array of tuples mapping atts to values.
def getGoalAttMap( provRID, provName, record, results, cursor ) :
  goalAttMap = []

  # grab all goal atts for this prov rule
  cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + provRID + "'" )
  res = cursor.fetchall()
  res = tools.toAscii_multiList( res )

  atts = []
  for r in res :
    attName = r[1]
    atts.append( attName )

  # grab the set of provenance records containing the input record.
  fullCandidateProvRecords = getFullCandidateProvRecords( provName, record, results )

  if len( fullCandidateProvRecords ) > 1 :
    print "**** WARNING ****\nMore than one provenance record partially matches the input record:\ninput record = " + str(record) + "\nprovenance records = " + str( fullCandidateProvRecords ) + "\npyLDFI currently handles only one provenance record per input record. In particular, the chosen provenance record is the first in the list of candidate provenance records."
  elif len( fullCandidateProvRecords ) < 1 :
    sys.exit( "**** FATAL ERROR ****\nNo provenance record partially matches the input record.\ninput record = " + str( record ) + "\nfull results = " + str(results) )

  else :
    fullProvRecord = fullCandidateProvRecords[0]

    if DEBUG :
      if provName.startswith( "missing_log" ) :
        sys.exit( "BREAKPOINT : fullCandidateProvRecords = " + str(fullCandidateProvRecords) )

    # map atts to values in tuples first
    # to align with ordering.
    for i in range( 0, len( atts ) ) :
      if i < len( atts ) :
        goalAttMap.append( ( atts[i], fullProvRecord[i] ) )
      else :
        goalAttMap.append( ( atts[i], None ) )

  return goalAttMap


#####################################
#  GET FULL CANDIDATE PROV RECORDS  #
#####################################
def getFullCandidateProvRecords( provName, record, results ) :
  candProvRecs = []

  provRes = results[ provName ]

  for rec in provRes :
    if checkContains( rec, record ) :
      candProvRecs.append( rec )

  return candProvRecs


##################
#  GET SUBGOALS  #
##################
# grab the subgoals+attributes lists from the appropriate prov rule
# return an array of tuples mapping subgoal names to info tuples
# info tuples are of the form ( isNeg, [ listOfAttStrings ] )
def getSubgoals( provRuleID, cursor ) :
  subgoalInfo = []

  # grab all subgoals for the prov rule
  cursor.execute( "SELECT subgoalName,sid FROM Subgoals WHERE rid=='" + provRuleID + "'" )
  subInfo = cursor.fetchall()
  subInfo = tools.toAscii_multiList( subInfo )

  # grab all the atts per subgoal
  # plus isNeg value.
  for sub in subInfo :
    name = sub[0]
    sid  = sub[1]

    cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + provRuleID + "' AND sid=='" + sid + "'" )
    attInfo = cursor.fetchall()
    attInfo = tools.toAscii_multiList( attInfo )

    cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid=='" + provRuleID + "' AND sid=='" + sid + "'" )
    negInfo = cursor.fetchall()
    negInfo = tools.toAscii_multiList( negInfo )

    # need to clean because created as a list of arrays containing only one string each.
    cleanNegInfo = []
    for n in negInfo :
      cleanNegInfo.append( n[0] )

    if len( cleanNegInfo ) >= 1 : 
      if not cleanNegInfo[0] == "notin" :
        sys.exit( "**** FATAL ERROR ****\nUnrecognized prefix argument to rule subgoal in " + str(cleanNegInfo) + "\nAborting..." )
    else :
      cleanNegInfo.append( "" ) # no prefix means subgoal is positive

    # ---------------------------------- #
    # sanity checks
    if len( attInfo ) < 1 :
      sys.exit( "**** FATAL ERROR ****\nNo attributes for subgoal " + name + "\nAborting..." )

    if len( cleanNegInfo ) > 1 :
      print "**** WARNING ****:\nMore than one additional prefix argument exists for the subgoal of a rule in the input program. The current version of pyLDFI only supports one optional prefix argument per subgoal, notin. Proceeding by taking the first additional argument by default."
    # ---------------------------------- #

    # clean up att list
    cleanList = []
    for att in attInfo :
      attID   = att[0]
      attName = att[1]
      cleanList.append( attName )

    # define subgoal info tuple
    newTup = ( name, cleanNegInfo[0], cleanList )
    subgoalInfo.append( newTup )

  return subgoalInfo


##################
#  GET PROV RID  #
##################
# choose the prov rid associated with a particular rule
# given the name of the rule, the seed record from the evaluation
# results, the full results, and the database cursor.
#
# get list of prov rids associated with rname
# iterate over contents of prov relations from full results.
# discover the tuple most closely matching the input record.
# Observe the schemas for all prov rules for a specific rule are identical.
# Furthermore, the schemas of the original rule and the prov rules are identical 
# up to the arity of the original rule for the first N fields of the schema (left-to-right)
#
def get_prov_rid_info( rname, record, fullResults, cursor ) :
  rid = None

  if DEBUG :
    print "... running getProvRID ..."
    print " rname       = " + str( rname )
    print " record      = " + str( record )
    print " fullResults = " + str( fullResults )
    #sys.exit( "BREAKPOINT1" )

  # get ids and names for all rules
  provName = rname + "_prov"
  cursor.execute( "SELECT rid,goalName FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_multiList( ridList )

  # grab the relevant prov rules only
  candidateRIDS = []
  for r in ridList :
    ident = r[0]
    name  = r[1]

    if name.startswith( provName ) :
      candidateRIDS.append( r )

  # iterate over relations per prov rule to find a partial match with record.
  validRIDS = []
  for r in candidateRIDS :

    ident       = r[0]
    name        = r[1]
    evalResults = fullResults[ name ]

    for res in evalResults :
      if checkContains( res, record ) :
        validRIDS.append( r )

  if len( validRIDS ) < 1 :
    sys.exit( "********************\n********************\nFATAL ERROR in file " + __name__ + " in function " + inspect.stack()[0][3] + " :\n>>> " + str(record) + "\ndoes match a record in the program output results for the provenance of rule\n>>> " + rname + "\nProgram results dump located at: " + C4_RESULTS_PATH )

  elif len( validRIDS ) > 1 :
    print "********************\n********************\nWARNING : Multiple rules exist which could have triggered the derivation of the record " + str(record) +  ". The current implementation solution picks the first one and hopes for the best. Future versions of pyLDFI will support a more robust picking method."
    rid = validRIDS[0]

  else :
    rid = validRIDS[0]

  return rid


####################
#  CHECK CONTAINS  #
####################
# check if rec1 contains rec2
# for provenance rules, the arity of the schema is equal to or
# greater than the arity of the original schema.
# furthermore, the attributes of both are semantically identical up to the 
# final (Nth most/rightmost) attribute of the original rule.
#
# rec1 := a provenance record
# rec2 := the given original record
#
# HANDLING WILDCARDS :
#   If record contains a wildcard ( represented as the string '__WILDCARD__' ),
#   then the check ignores the components at the wildcard index.
#
def checkContains( rec1, rec2 ) :

  if DEBUG :
    print "rec1 = " + str( rec1 ) 
    print "rec2 = " + str( rec2 ) 

  # check if original record contains a wildcard.
  # if so, grab the index.
  wildcardIndexes = []
  if "__WILDCARD__" in rec2 :
    for i in range( 0, len( rec2 ) ) : 
      currRecordVal = rec2[i]
      if "__WILDCARD__" in currRecordVal :
        wildcardIndexes.append( i )

  for i in range( 0, len(rec2) ) :
    if not i in wildcardIndexes :
      if rec2[i] == rec1[i] :
        pass
      else :
        return False

  return True


#########
#  EOF  #
#########
