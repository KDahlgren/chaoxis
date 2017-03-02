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


##################
#  GET ORIG RID  #
##################
def getOrigRID( provRID, provName, cursor ) :
  rid = None

  # ------------------------------------------------------- #
  # get complete attList for provRID
  cursor.execute( "SELECT SubgoalAtt.attID,SubgoalAtt.attName FROM Rule,Subgoals,SubgoalAtt WHERE Rule.rid==Subgoals.rid AND Subgoals.sid==SubgoalAtt.sid AND Rule.ridi='" + provRID + "'" )
  attList_provRID = cursor.fetchall()
  attList_provRID = tools.toAscii_multiList( attList_provRID )

  # ------------------------------------------------------- #
  # get list of candidate original rule ids

  # get original name
  tmp      = provName.split( "_prov" )
  origName = tmp[0]

  # get ids and names for all rules
  cursor.execute( "SELECT rid,goalName FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_multiList( ridList )

  # grab ids for rules labeled with the original name
  candidateRIDS = []
  for r in ridList :
    candid = r[0]
    name  = r[1]
    if name == origName :
      candidateRIDS.append( candid )

  # ------------------------------------------------------- #
  # find the original rule with matching attList

  print "candidateRIDS = " + str( candidateRIDS )

  for candid in candidateRIDS :
    # grab the att list for this rule
    cursor.execute( "SELECT SubgoalAtt.attID,SubgoalAtt.attName FROM Rule,Subgoals,SubgoalAtt WHERE Rule.rid==Subgoals.rid AND Subgoals.sid==SubgoalAtt.sid AND Rule.rid=='" + candid + "'" )
    attList_candid = cursor.fetchall()
    attList_candid = tools.toAscii_multiList( attList_candid )

    print "attList_candid = " + str( attList_candid )
    print "attList_gname  = " + str( attList_gname )

    if checkEquality( attList_gname, attList_candid ) :
      print "returning candid = " + candid
      return candid

  # otherwise, no provenance rule matches =[
  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: could not find matching provenance rule for " + gname )

  return rid


#########################
#  GET PARTIAL MATCHES  #
#########################
# get the set of tuples from the 'name' relation
# satisfying the wildcard.
def getPartialMatches( name, record, results ) :
  partialMatches = []

  # get results for this goal name
  res = results[ name ]

  # iterate over all relation tuples in results
  for tup in res :

    yesValidPatrialMatch = True # be optimisitc! ^.^

    for i in range(0,len(tup)) :
      currTupData = tup[i]
      currRecData = record[i]

      # (explicitly defining cases for clarity)
      # case match
      if currTupData == currRecData :
        pass

      # case wildcard in record
      elif currRecData == "__WILDCARD__" :
        pass

      # case invalidating partial match
      elif (not currTupData == currRecData) and (not currRecData == "__WILDCARD__"):
        yesValidPatrialMatch = False

      # something weird happened. maybe someone tried to change the __WILDCARD__ constant...
      else :
        sys.exit( "********************\n********************\nFATAL ERROR in file " + __name__ + " in function " + inspect.stack()[0][3] + " :\n>>> " + " Attempting to find partial matches for wilcard record, where wildcards are defined as '__WILDCARD__', but encoutered a case in which aligned data are (1) not equal, (2) the aligned data item in record is not a wildcard, and (3) the data items are equal or the aligned data item in record is a wildcard. \nPlease see the alignment record and attempted result match :\nrecord = " + str(record) + "\nattempted partial match = " + str(tup) )

    if yesValidPatrialMatch :
      partialMatches.append( tup )

  return partialMatches


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
  goalAttMap = {}

  # ---------------------------------------------------------------- #
  # grab all goal atts for this prov rule
  cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + provRID + "'" )
  res = cursor.fetchall()
  res = tools.toAscii_multiList( res )

  attNames = []
  for r in res :
    name = r[1]
    attNames.append( name )

  # ---------------------------------------------------------------- #
  # match attNames with vals from the record

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
# choose the prov rid associated with a particular goal
# given the name of the goal, the seed record from the evaluation
# results, the full results, and the database cursor.
#
# get list of prov rids associated with gname and
# iterate over contents of prov relations from full results.
# discover the tuple most closely matching the input record.
#
def get_prov_rid_info( gname, record, fullResults, cursor ) :
  rid = None

  if DEBUG :
    print "... running get_prov_rid_info ..."
    print " gname       = " + str( gname )
    print " record      = " + str( record )
    print " fullResults = " + str( fullResults )

  # ------------------------------------------------------- #
  # get complete attList for gname
  cursor.execute( "SELECT SubgoalAtt.attID,SubgoalAtt.attName FROM Rule,Subgoals,SubgoalAtt WHERE Rule.rid==Subgoals.rid AND Subgoals.sid==SubgoalAtt.sid AND Rule.goalName=='" + gname + "'" )
  attList_gname = cursor.fetchall()
  attList_gname = tools.toAscii_multiList( attList_gname )

  # ------------------------------------------------------- #
  # get list of candidate provenance rule ids

  # get ids and names for all rules
  provName = gname + "_prov"
  cursor.execute( "SELECT rid,goalName FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_multiList( ridList )

  # grab ids for prov rules related to gname
  candidateRIDS = []
  for r in ridList :
    candid = r[0]
    name  = r[1]
    if name.startswith( provName ) :
      candidateRIDS.append( candid )

  # ------------------------------------------------------- #
  # find the prov rule with matching attList

  print "candidateRIDS = " + str( candidateRIDS )

  for candid in candidateRIDS :
    # grab the att list for this rule
    cursor.execute( "SELECT SubgoalAtt.attID,SubgoalAtt.attName FROM Rule,Subgoals,SubgoalAtt WHERE Rule.rid==Subgoals.rid AND Subgoals.sid==SubgoalAtt.sid AND Rule.rid=='" + candid + "'" )
    attList_candid = cursor.fetchall()
    attList_candid = tools.toAscii_multiList( attList_candid )

    print "attList_candid = " + str( attList_candid )
    print "attList_gname  = " + str( attList_gname )

    if checkEquality( attList_gname, attList_candid ) :
      print "returning candid = " + candid
      return candid

  # otherwise, no provenance rule matches =[
  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: could not find matching provenance rule for " + gname )


####################
#  CHECK EQUALITY  #
####################
# check if the complete att list of the original rule
# is a subset of the complete att list of the candidate
# provenance rule (future work: should probably be an
# equivalent set)
def checkEquality( attList_gname, attList_candid ) :

  for att in attList_gname :
    if not att in attList_candid :
      return False

  return True


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
