#!/usr/bin/env python

'''
dumpers.py
   Methods for dumping specific contents from the database.
'''

import inspect, os, sys
import tools


#############
#  GLOBALS  #
#############
DUMPERS_DEBUG = tools.getConfig( "UTILS", "DUMPERS_DEBUG", bool )


###############
#  RULE DUMP  #
###############
# input database cursor
# output nothing, print all rules to stdout
def ruleDump( cursor ) :

  if DUMPERS_DEBUG :
    print "********************\nProgram Rules :"

  rules = []

  # --------------------------------------------------------------- #
  #                           GOALS                                 #

  # get all rule ids
  cursor.execute( "SELECT rid FROM Rule" )
  ruleIDs = cursor.fetchall()
  ruleIDs = tools.toAscii_list( ruleIDs )

  # iterate over rule ids
  newRule = []
  for i in ruleIDs :
    cursor.execute( "SELECT goalName FROM Rule WHERE rid == '" + i + "'" ) # get goal name
    goalName    = cursor.fetchone()
    goalName    = tools.toAscii_str( goalName )

    # get list of attribs in goal
    goalList    = cursor.execute( "SELECT attName FROM GoalAtt WHERE rid == '" + i + "'" )# list of goal atts
    goalList    = tools.toAscii_list( goalList )

    # get goal time arg
    goalTimeArg = ""
    cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + i + "'" )
    goalTimeArg = cursor.fetchone()
    goalTimeArg = tools.toAscii_str( goalTimeArg )

    # convert goal info to pretty string
    newRule.append( goalName + "(" )
    for j in range(0,len(goalList)) :
      if j < (len(goalList) - 1) :
        newRule.append( goalList[j] + "," )
      else :
        newRule.append( goalList[j] + ")" )
    if not goalTimeArg == "" :
      newRule.append( "@" + goalTimeArg + " :- " )
    else :
      newRule.append( " :- " )

    # --------------------------------------------------------------- #
    #                         SUBGOALS                                #

    # get list of sids for the subgoals of this rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid == '" + str(i) + "'" ) # get list of sids for this rule
    subIDs = cursor.fetchall()
    subIDs = tools.toAscii_list( subIDs )

    # iterate over subgoal ids
    for k in range(0,len(subIDs)) :
      s = subIDs[k]

      # get subgoal name
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + str(i) + "' AND sid == '" + str(s) + "'" )
      subgoalName = cursor.fetchone()

      if not subgoalName == None :
        subgoalName = tools.toAscii_str( subgoalName )

        if DUMPERS_DEBUG :
          print "subgoalName = " + subgoalName

        # get subgoal attribute list
        subAtts = cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + i + "' AND sid == '" + s + "'" )
        subAtts = tools.toAscii_list( subAtts )

        # get subgoal time arg
        cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + i + "' AND sid == '" + s + "'" ) # get list of sids for this rule
        subTimeArg = cursor.fetchone() # assume only one additional arg
        subTimeArg = tools.toAscii_str( subTimeArg )

        # get subgoal additional args
        cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + i + "' AND sid == '" + s + "'" ) # get list of sids for this rule
        subAddArg = cursor.fetchone() # assume only one additional arg
        if not subAddArg == None :
          subAddArg = tools.toAscii_str( subAddArg )
          subAddArg += " "
          newRule.append( subAddArg )

        # all subgoals have a name and open paren
        newRule.append( subgoalName + "(" )

        # add in all attributes
        for j in range(0,len(subAtts)) :
          if j < (len(subAtts) - 1) :
            newRule.append( subAtts[j] + "," )
          else :
            newRule.append( subAtts[j] + ")" )

        # conclude with time arg, if applicable
        if not subTimeArg == "" :
          newRule.append( "@" + subTimeArg )

        # cap with a comma, if applicable
        if k < len( subIDs ) - 1 :
          newRule.append( "," )

    # --------------------------------------------------------------- #
    #                         EQUATIONS                               #

    cursor.execute( "SELECT eid,eqn FROM Equation WHERE rid=='" + i + "'" ) # get list of eids for this rule
    eqnList = cursor.fetchall()
    eqnList = tools.toAscii_multiList( eqnList )

    for e in eqnList :
      eid = e[0]
      eqn = e[1]
      newRule.append( "," + str(eqn) )

    # --------------------------------------------------------------- #

    newRule.append( " ;" ) # end all rules with a semicolon
    rules.append( newRule )
    newRule = []

  # print rules
  if DUMPERS_DEBUG :
    for r in rules :
      print ''.join(r)


###############
#  FACT DUMP  #
###############
# input database cursor
# output nothing, print all facts to stdout
def factDump( cursor ) :

  if DUMPERS_DEBUG :
    print "********************\nProgram Facts :"

  facts = []

  # get all fact ids
  cursor.execute( "SELECT fid FROM Fact" )
  factIDs = cursor.fetchall()
  factIDs = tools.toAscii_list( factIDs )

  # iterate over fact ids
  newFact = []
  for i in factIDs :
    cursor.execute( "SELECT name FROM Fact WHERE fid == '" + str(i) + "'" ) # get fact name
    factName    = cursor.fetchone()
    factName    = tools.toAscii_str( factName )

    # get list of attribs in fact
    factList    = cursor.execute( "SELECT attName FROM FactAtt WHERE fid == '" + str(i) + "'" ) # list of fact atts
    factList    = tools.toAscii_list( factList )

    # get fact time arg
    factTimeArg = ""
    cursor.execute( "SELECT timeArg FROM Fact WHERE fid == '" + i + "'" )
    factTimeArg = cursor.fetchone()
    factTimeArg = tools.toAscii_str( factTimeArg )

    # convert fact info to pretty string
    newFact.append( factName + "(" )
    for j in range(0,len(factList)) :
      if j < (len(factList) - 1) :
        newFact.append( factList[j] + "," )
      else :
        newFact.append( factList[j] + ")" )
    if not factTimeArg == "" :
      newFact.append( "@" + factTimeArg )

    newFact.append( " ;" ) # end all facts with a semicolon
    facts.append( newFact )
    newFact = []

  # print facts
  for f in facts :
    if DUMPERS_DEBUG :
      print ''.join(f)


################
#  CLOCK DUMP  #
################
# input db cursor
# output nothing, print all clock entries to stdout
def clockDump( cursor ) :

  print "********************\nProgram Clock :"
  clock = cursor.execute('''SELECT * FROM Clock''')

  for c in clock :
    print c


######################
#  RECONSTRUCT RULE  #
######################
def reconstructRule( rid, cursor ) :

  if DUMPERS_DEBUG :
    print "... running reconstructRule ..."

  rule = ""

  # -------------------------------------------------------------- #
  #                           GOAL                                 #
  # -------------------------------------------------------------- #
  #
  # get goal name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid == '" + rid + "'" ) # get goal name
  goalName    = cursor.fetchone()
  goalName    = tools.toAscii_str( goalName )

  # get list of attribs in goal
  goalList    = cursor.execute( "SELECT attName FROM GoalAtt WHERE rid == '" + rid + "'" )# list of goal atts
  goalList    = tools.toAscii_list( goalList )

  # get goal time arg
  goalTimeArg = ""
  cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + rid + "'" )
  goalTimeArg = cursor.fetchone()
  goalTimeArg = tools.toAscii_str( goalTimeArg )

  # convert goal info to string
  rule += goalName + "("
  for j in range(0,len(goalList)) :
    if j < (len(goalList) - 1) :
      rule += goalList[j] + ","
    else :
      rule += goalList[j] + ")"
  if not goalTimeArg == "" :
    rule += "@" + goalTimeArg + " :- "
  else :
    rule += " <= "

  # --------------------------------------------------------------- #
  #                         SUBGOALS                                #
  # --------------------------------------------------------------- #
  #

  # get list of sids for the subgoals of this rule
  cursor.execute( "SELECT sid FROM Subgoals WHERE rid == '" + rid + "'" ) # get list of sids for this rule
  subIDs = cursor.fetchall()
  subIDs = tools.toAscii_list( subIDs )

  # iterate over subgoal ids
  for k in range(0,len(subIDs)) :
    newSubgoal = ""

    s = subIDs[k]

    # get subgoal name
    cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + str(rid) + "' AND sid == '" + str(s) + "'" )
    subgoalName = cursor.fetchone()

    if not subgoalName == None :
      subgoalName = tools.toAscii_str( subgoalName )

      if DUMPERS_DEBUG :
        print "subgoalName = " + subgoalName

      # get subgoal attribute list
      subAtts = cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + rid + "' AND sid == '" + s + "'" )
      subAtts = tools.toAscii_list( subAtts )

      # get subgoal time arg
      cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + rid + "' AND sid == '" + s + "'" ) # get list of sids for this rule
      subTimeArg = cursor.fetchone() # assume only one additional arg
      subTimeArg = tools.toAscii_str( subTimeArg )

      # get subgoal additional args
      subAddArg = None
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + rid + "' AND sid == '" + s + "'" ) # get list of sids for this rule
      subAddArg = cursor.fetchone() # assume only one additional arg
      if subAddArg :
        subAddArg = tools.toAscii_str( subAddArg )
        subAddArg += " "
        newSubgoal += subAddArg

      # all subgoals have a name and open paren
      newSubgoal += subgoalName + "("

      # add in all attributes
      for j in range(0,len(subAtts)) :
        if j < (len(subAtts) - 1) :
          newSubgoal += subAtts[j] + ","
        else :
          newSubgoal += subAtts[j] + ")"

      # cap with a comma, if applicable
      if k < len( subIDs ) - 1 :
        newSubgoal += ","

    rule += newSubgoal

  # --------------------------------------------------------------- #
  #                         EQUATIONS                               #
  # --------------------------------------------------------------- #

  cursor.execute( "SELECT eid,eqn FROM Equation WHERE rid=='" + rid + "'" ) # get list of eids for this rule
  eqnList = cursor.fetchall()
  eqnList = tools.toAscii_multiList( eqnList )

  for e in eqnList :
    eid = e[0]
    eqn = e[1]
    rule += "," + str(eqn)

  # --------------------------------------------------------------- #

  rule += " ;" # end all rules with a semicolon

  return rule

#########
#  EOF  #
######### 
