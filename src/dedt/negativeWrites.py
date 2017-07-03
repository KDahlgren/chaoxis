#!/usr/bin/env python

'''
negativeWrites.py
   Define the functionality for collecting the provenance of negative subgoals.
'''

import inspect, os, string, sys
import sympy

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( __file__ + "/../.." )

from utils import clockTools, tools, dumpers
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
NEGATIVEWRITES_DEBUG = tools.getConfig( "DEDT", "NEGATIVEWRITES_DEBUG", bool )


#####################
#  NEGATIVE WRITES  #
#####################
def negativeWrites( cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running negative writes ..."

  setNegativeRules(   cursor )
  #setFactComplements( cursor )

  # dump to test
  if NEGATIVEWRITES_DEBUG :
    print
    print "<><><><><><><><><><><><><><><><><><>"
    print ">>> DUMPING FROM negativeWrites <<<"
    print "<><><><><><><><><><><><><><><><><><>"
    dumpers.programDump(  cursor )


########################
#  SET NEGATIVE RULES  #
########################
def setNegativeRules( cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running set negative rules ..."

  # ------------------------------------------------- #
  # get all negated subgoals

  # get all subgoals with additional arguments
  cursor.execute( "SELECT Rule.rid, Subgoals.sid, subgoalName, argName FROM Rule, Subgoals, SubgoalAddArgs WHERE Rule.rid==Subgoals.rid AND Rule.rid== SubgoalAddArgs.rid AND Subgoals.sid== SubgoalAddArgs.sid" )
  data = cursor.fetchall()
  data = tools.toAscii_multiList( data )

  # filter on "notin", meaning the subgoal is negated
  rulesWithNegatedSubgoals = []
  for d in data :
    if d[3] == "notin" :
      rulesWithNegatedSubgoals.append( d )

  # ------------------------------------------------- #
  # get all datalog rules associated with each subgoal
  negatedRulesMap = {}
  for rule in rulesWithNegatedSubgoals :

    rid         = rule[0]
    sid         = rule[1]
    subgoalName = rule[2]

    # ------------------------------------------------- #
    # get all rules per subgoal
    cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + subgoalName + "'" )
    allSubgoalRuleIDs = cursor.fetchall()
    allSubgoalRuleIDs = tools.toAscii_list( allSubgoalRuleIDs )

    negatedRulesMap[ subgoalName ] = allSubgoalRuleIDs

  # ------------------------------------------------- #
  # generate additional new rules per negated subgoal 
  # rules via DeMorgan's Law

  DM_Rules_all = doDeMorgans( negatedRulesMap, cursor )

  # ------------------------------------------------- #
  # replace negated subgoal names in original rules 
  # with positive subgoals prefixed with 'NOT_'

  replaceNegSubgoals( cursor )

  # ------------------------------------------------- #


##########################
#  REPLACE NEG SUBGOALS  #
##########################
def replaceNegSubgoals( cursor ) :

  # get all rids
  cursor.execute( "SELECT rid,goalName FROM Rule" )
  goalData = cursor.fetchall()
  goalData = tools.toAscii_multiList( goalData )

  # create a map for convenience
  ridToName_map = {}
  for data in goalData :
    rid      = data[0]
    goalName = data[1]
    ridToName_map[ rid ] = goalName

  allRIDs = [ data[0] for data in goalData ] # grab list of rids only

  # examine subgoals per rule
  for rid in allRIDs :

    ####################################
    # EXPERIMENT :                     #
    # pushes negations to leaves       #
    if "DM_" in ridToName_map[ rid ] : #
      continue                         #
    ####################################

    # get all subgoals and subgoal names in this rule
    cursor.execute( "SELECT sid,subgoalName FROM Subgoals WHERE rid='" + rid + "'" )
    subgoalData = cursor.fetchall()
    subgoalData = tools.toAscii_multiList( subgoalData )

    # create dict for convenience
    subgoalIDToName_dict = {}
    for sub in subgoalData :
      sid                         = sub[0]
      subgoalName                 = sub[1]
      subgoalIDToName_dict[ sid ] = subgoalName

    # get list of fact names
    cursor.execute( "SELECT name FROM Fact" )
    allFactNames = cursor.fetchall()
    allFactNames = tools.toAscii_list( allFactNames )

    # grab list of sids only
    allSIDs = [ data[0] for data in subgoalData ]

    # get additional args for all subgoals in this rule
    addArgs_dict = {}
    for sid in allSIDs :

      ##################################################
      # EXPERIMENT :                                   #
      # pushes negations to leaves                     #
      if subgoalIDToName_dict[ sid ] in allFactNames : #
        continue                                       #
      ##################################################

      cursor.execute( "SELECT sid,argName FROM SubgoalAddArgs WHERE rid='" + rid + "' AND sid='" + sid + "'" )
      addArgs = cursor.fetchall()
      addArgs = tools.toAscii_multiList( addArgs )
      for arg in addArgs :
        sid     = arg[0]
        argName = arg[1]
        addArgs_dict[ sid ] = argName

    # check if subgoal is negated
    for subgoal in subgoalData :
      sid         = subgoal[0]
      subgoalName = subgoal[1]

      if sid in addArgs_dict :
        if addArgs_dict[ sid ] == "notin" :
          # update subgoal name
          newSubgoalName = "NOT_" + subgoalName
          cursor.execute( "UPDATE Subgoals SET subgoalName=='" + newSubgoalName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

          # update subgoal additional arg (i.e. erase the notin)
          cursor.execute( "UPDATE SubgoalAddArgs SET argName=='' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )


##################
#  DO DEMORGANS  #
##################
def doDeMorgans( negatedRulesMap, cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running do demorgans ..."

  # ----------------------------------------------------------- #
  # combine all rules for each rule name into a single 
  # sympy formula string

  ruleNameToPosFmlaStr_map = {}
  predToID_perRule_map     = {}
  for ruleName in negatedRulesMap :
    ruleRIDs = negatedRulesMap[ ruleName ]

    predicateToID_map  = {}
    ridSidToPredicate_map = {}

    # ////////////////////////////////////////// #
    # get all rule data
    for rid in ruleRIDs :

      # get list of all sids for this rid
      cursor.execute( "SELECT sid FROM Subgoals WHERE rid='" + rid + "'" )
      sidList = cursor.fetchall()
      sidList = tools.toAscii_list( sidList )

      # map sids to sign
      signMap = {}
      for sid in sidList :
        cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid='" + rid + "' AND sid='" + sid + "'" )
        sign = cursor.fetchone()
        if sign :
          sign = tools.toAscii_str( sign )
        signMap[ sid ] = sign

      for sid in sidList :
        sign = signMap[ sid ]

        # get a random identifier string
        predID = tools.getID()

        # map predIDs to rids and sids
        predicateToID_map[ predID ] = [ rid, [ sign, sid ] ]

        # map rids and sids to predIDs
        if sign == "notin" :
          key = rid + ",_NEG_" + sid
        else :
          key = rid + "," + sid
        ridSidToPredicate_map[ key ] = predID

    predToID_perRule_map[ ruleName ] = predicateToID_map

    # ////////////////////////////////////////// #
    # convert to sympy formula
    ruleConjuncts_map = {}
    for key in ridSidToPredicate_map :
      predID = ridSidToPredicate_map[ key ]
      key    = key.split( "," )
      rid    = key[0]
      sid    = key[1]
      sign   = None
      if "_NEG_" in sid :
        sid  = sid.replace( "_NEG_", "" )
        sign = "_NEG_"

      if rid in ruleConjuncts_map :
        currConjunct_str = ruleConjuncts_map[ rid ]
        if sign :
          ruleConjuncts_map[ rid ] = currConjunct_str + " & ~( " + predID + " )"
        else :
          ruleConjuncts_map[ rid ] = currConjunct_str + " & " + predID
      else :
        if sign :
          ruleConjuncts_map[ rid ] = "~( " + predID + " )"
        else :
          ruleConjuncts_map[ rid ] = predID

    # add parens
    for rid in ruleConjuncts_map :
      conjunct_str = ruleConjuncts_map[ rid ]
      ruleConjuncts_map[ rid ] = "( " + conjunct_str + " )"

    # build positive DNF fmla
    posFmla = None
    for key in ruleConjuncts_map :
      if posFmla :
        posFmla += " | " + ruleConjuncts_map[key]
      else :
        posFmla = ruleConjuncts_map[key]

    # save positive DNF fmla
    ruleNameToPosFmlaStr_map[ ruleName ] = posFmla

  # ----------------------------------------------------------- #
  # negate sympy formulas and simplify into DNF

  # negate
  ruleNameToNegFmlaStr_map = {}
  for ruleName in ruleNameToPosFmlaStr_map :
    posFmla = ruleNameToPosFmlaStr_map[ ruleName ]
    if posFmla :
      negFmla = "~( " + posFmla + " )"
    else :
      negFmla = None
    ruleNameToNegFmlaStr_map[ ruleName ] = negFmla

  # simplify
  ruleNameToNegFmlaStr_simplified_map = {}
  for ruleName in ruleNameToNegFmlaStr_map :
    negFmla    = ruleNameToNegFmlaStr_map[ ruleName ]
    simplified = sympy.to_dnf( negFmla )
    ruleNameToNegFmlaStr_simplified_map[ ruleName ] = simplified 

  # ----------------------------------------------------------- #
  # save a new rule to IR db per disjunct

  setNewRules( ruleNameToNegFmlaStr_simplified_map, predToID_perRule_map, cursor )

  # ----------------------------------------------------------- #



###################
#  SET NEW RULES  #
###################
# input DNF string
# output array of clauses of conjuncted predicate ID literals
def setNewRules( ruleNameToNegFmlaStr_simplified_map, predToID_perRule_map, cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running set new rules ..."

  # each negated rule spawns 1 or more new rules, depending upon number of disjuncts
  # each clause corresponds to a new rule
  for ruleName in ruleNameToNegFmlaStr_simplified_map :

    # only add new rules for negated IDBs
    if not ruleNameToNegFmlaStr_simplified_map[ ruleName ] :
      continue

    newName     = "DM_" + ruleName
    newGoalAtts = [] # populate with all variables appearing in all subgoals
    newRIDs     = []

    # get clauses for this rule
    negated_simplified_fmla_str = str( ruleNameToNegFmlaStr_simplified_map[ ruleName ] )
    negated_simplified_fmla_str = negated_simplified_fmla_str.translate( None, string.whitespace)
    negated_simplified_fmla_str = negated_simplified_fmla_str.replace( "(", "" )
    negated_simplified_fmla_str = negated_simplified_fmla_str.replace( ")", "" )
    clauses                     = negated_simplified_fmla_str.split( "|" )

    # get pred ID mapping for this rule
    predMap = predToID_perRule_map[ ruleName ]

    # spawn one new DM_ rule per clause
    for c in clauses :
      newRID = tools.getID()
      newRIDs.append( newRID )
      literalList = c.split( "&" )
      for literal in literalList :
        if "~" in literal :
          predicate = literal.replace( "~", "" )
          addArg = "notin"
        else :
          predicate = literal
          addArg = None

        predData  = predMap[ predicate ]
        rid       = predData[0]
        sign      = predData[1][0]
        sid       = predData[1][1]

        # -------------------------------------------- #
        # reconstruct subgoal

        # get name and time arg
        cursor.execute( "SELECT subgoalName,subgoalTimeArg FROM Subgoals WHERE rid='" + rid + "' AND sid='" + sid + "'"  )
        data           = cursor.fetchall()
        data           = tools.toAscii_multiList( data )
        subgoalName    = data[0][0]
        subgoalTimeArg = data[0][1]

        # get subgoal attribute list
        cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid='" + rid + "' AND sid='" + sid + "'" )
        subgoalAtts = cursor.fetchall()
        subgoalAtts = tools.toAscii_multiList( subgoalAtts )

        # get subgoal additional arguments
        #cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid='" + rid + "' AND sid='" + sid + "'" )
        #addArg = cursor.fetchone()
        #if addArg :
        #  addArg = tools.toAscii_str( addArg )

        # -------------------------------------------- #
        # save subgoal with the rid of the new rule

        # create new sid
        newSID = tools.getID()

        # save subgoal name and time arg
        cursor.execute( "INSERT INTO Subgoals VALUES ('" + newRID + "','" + newSID + "','" + subgoalName + "','" + subgoalTimeArg + "')" )

        # save subgoal attributes
        for att in subgoalAtts :
          attID        = att[0]
          attName      = att[1]
          attType      = att[2]
          goalAttNames = [ x[0] for x in newGoalAtts ]

          if not attName in goalAttNames and not attName == "_" :
            newGoalAtts.append( [ attName, attType ] )

          cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + newRID + "','" + newSID + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

        # save subgoal additional args
        if addArg :
          cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + newRID + "','" + newSID + "','" + str( addArg ) + "')")
        else :
          cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + newRID + "','" + newSID + "','')")

    # -------------------------------------------- #
    # save new goal data

    for newRID in newRIDs :
      # save new goal name and rewritten status
      timeArg       = ""
      rewrittenFlag = True
      cursor.execute( "INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + newRID + "','" + newName + "','" + timeArg + "','" + str(rewrittenFlag) + "')" )

      # save new goal attributes
      attID = 0
      for attData in newGoalAtts :
        attName = attData[0]
        attType = attData[1]
        cursor.execute( "INSERT INTO GoalAtt VALUES ('" + newRID + "','" + str(attID) + "','" + attName + "','" + attType + "')" )
        attID += 1

    # -------------------------------------------- #
    # save necessary equations per goal

    for newRID in newRIDs :

      # get goal att list
      cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid='" + newRID + "'" )
      goalAttList = cursor.fetchall()
      goalAttList = tools.toAscii_multiList( goalAttList )

      # get att list derived from all subgoals
      cursor.execute( "SELECT sid FROM Subgoals WHERE rid='" + newRID + "'" )
      thisSubgoalList = cursor.fetchall()
      thisSubgoalList = tools.toAscii_multiList( thisSubgoalList )
      thisSubgoalList = [ sidArray[0] for sidArray in thisSubgoalList ]

      subgoalAttList = []
      for sid in thisSubgoalList :
        cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid='" + newRID + "' AND sid='" + sid + "'" )
        data    = cursor.fetchall()
        data    = tools.toAscii_multiList( data )

        for att in data :
          attName = att[1]
          attType = att[2]

          if not [ attName, attType ] in subgoalAttList :
            subgoalAttList.append( [ attName, attType ] )

      for attData in goalAttList :
        appears = False
        attName = attData[1]
        attType = attData[2]
        for sattData in subgoalAttList :
          sattName = sattData[0]
          sattType = sattData[1]
          if attName == sattName :
            appears = True
        if not appears :
          eid = tools.getID()
          eqn = attName + "=="
          if attType == 'int' :
            eqn += "-9999999999"
          else :
            eqn += '"None"'

          # insert equation
          cursor.execute( "INSERT INTO Equation VALUES ('" + newRID + "','" + eid + "','" + eqn + "')" )


    # --------------------------------------------------------------------- #
    # add NOT_R :- DM_R for all rules associated with a negative write

    notName = "NOT_" + ruleName
    notRID  = tools.getID()

    # get goal atts for original rule
    cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + ruleName + "'" )
    rid = cursor.fetchone()
    rid = tools.toAscii_str( rid )

    cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid='" + rid + "'" )
    goalAttList_orig = cursor.fetchall()
    goalAttList_orig = tools.toAscii_multiList( goalAttList_orig )

    # get goal att list for DM rules
    cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid='" + newRID[0] + "'" )
    goalAttList_dm = cursor.fetchall()
    goalAttList_dm = tools.toAscii_multiList( goalAttList )

    # -------------------- #
    # create NOT_ rule

    # insert notRID, notName, timeArg, and rewritten
    timeArg   = ""
    rewritten = True
    cursor.execute( "INSERT INTO Rule VALUES ('" + notRID + "','" + notName + "','" + timeArg + "','" + str( rewritten ) + "')" )

    # insert goal attributes
    for att in goalAttList_orig : 
      attID   = att[0]
      attName = att[1]
      attType = att[2]
      cursor.execute( "INSERT INTO GoalAtt VALUES ('" + notRID + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

    # insert subgoal info
    dm_sid         = tools.getID()
    subgoalName    = "DM_" + ruleName
    subgoalTimeArg = ""
    cursor.execute( "INSERT INTO Subgoals VALUES ('" + notRID + "','" + dm_sid + "','" + subgoalName + "','" + subgoalTimeArg + "')" )

    # insert subgoal attributes
    for att in goalAttList_dm :
      attID   = att[0]
      attName = att[1]
      attType = att[2]
      cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + notRID + "','" + dm_sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

    # insert equations
    for attData in goalAttList_orig :
      appears = False
      attName = attData[1]
      attType = attData[2]
      for dmattData in goalAttList_dm :
        dmattName = dmattData[0]
        dmattType = dmattData[1]
        if attName == dmattName :
          appears = True
      if not appears :
        eid = tools.getID()
        eqn = attName + "=="
        if attType == 'int' :
          eqn += "-9999999999"
        else :
          eqn += '"None"'

        cursor.execute( "INSERT INTO Equation VALUES ('" + notRID + "','" + eid + "','" + eqn + "')" )

    # --------------------------------------------------------------------- #


##########################
#  SET FACT COMPLEMENTS  #
##########################
# get names and schemas for all program facts
# define default contents for complementary tables ( NOT_factTable )
# save contents for new tables to Fact and FactAtt
# handle clock complement separately in a later step. Essential NOT_clock = all clock facts not included in clock.
def setFactComplements( cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running set fact complements ..."

  # get identifying info for all program facts
  cursor.execute( "SELECT fid,name,timeArg FROM Fact" )
  factData = cursor.fetchall()
  factData = tools.toAscii_multiList( factData )

  for fact in factData :
    fid     = fact[0]
    name    = fact[1]
    timeArg = fact[2]

    # get schema info for all program facts
    cursor.execute( "SELECT fid,attID,attName,attType FROM FactAtt WHERE fid='" + fid + "'" )
    factSchema = cursor.fetchall()
    factSchema = tools.toAscii_multiList( factSchema )

    print factSchema


  tools.bp( __name__, inspect.stack()[0][3], "break here." )


#########
#  EOF  #
#########
