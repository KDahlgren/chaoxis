#!/usr/bin/env python

'''
dedalusRewriter.py
   Define the functionality for rewriting Dedalus into datalog.
'''

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDALUSREWRITER_DEBUG = True

###########
#  CLEAN  #
###########
def clean( sqlresults ) :
  cleanResults = []
  for r in sqlresults :
    asciiResult = r[0].encode('utf-8')
    cleanResults.append( asciiResult )

  return cleanResults

###############
#  RULE DUMP  #
###############
def ruleDump( cursor ) :
  rules = []

  # get all rule ids
  cursor.execute( "SELECT rid FROM Rule" )
  ruleIDs = cursor.fetchall()
  ruleIDs = clean( ruleIDs )

  # iterate over rule ids
  newRule = []
  for i in ruleIDs :
    cursor.execute( "SELECT goalName    FROM Rule WHERE rid == '" + i + "'" ) # get goal name
    goalName    = cursor.fetchone()
    goalName    = goalName[0].encode('utf-8')
    goalList    = cursor.execute( "SELECT attName     FROM GoalAtt WHERE rid == '" + i + "'" )# list of goal atts
    goalList    = clean( goalList )
    cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + i + "'" )
    goalTimeArg = cursor.fetchone()
    goalTimeArg = goalTimeArg[0].encode('utf-8')

    newRule.append( goalName + "(" )
    for g in goalList :
      newRule.append( g + "," )
    newRule.append( ")@" + goalTimeArg + " :- " )

    cursor.execute( "SELECT sid FROM Subgoals" ) # get list of sids for this rule
    subIDs = cursor.fetchall()
    subIDs = clean( subIDs )

    for s in subIDs :
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + i + "' AND sid == '" + s + "'" )
      subgoalName = cursor.fetchone()

      if not subgoalName == None :
        subgoalName = subgoalName[0].encode('utf-8')
        subAtts = cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + i + "' AND sid == '" + s + "'" )
        subAtts = clean( subAtts )
        cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE sid == '" + s + "'" ) # get list of sids for this rule
        subTimeArg = cursor.fetchone()
        subTimeArg = subTimeArg[0].encode('utf-8')

        newRule.append( subgoalName + "(" )
        for g in subAtts :
          newRule.append( g + "," )
        newRule.append( ")@" + subTimeArg + ", " )

    rules.append( newRule )
    newRule = []

  for r in rules :
    print ''.join(r)

############################
#  GET DEDUCTIVE RULE IDS  #
############################
def getDeductiveRuleIDs( cursor ) :
  cursor.execute( '''SELECT rid FROM Rule WHERE NOT goalTimeArg == "next" AND NOT goalTimeArg == "async"''' )
  return cursor.fetchall()

############################
#  GET INDUCTIVE RULE IDS  #
############################
def getInductiveRuleIDs( cursor ) :
  cursor.execute( '''SELECT rid FROM Rule WHERE goalTimeArg == "next"''' )
  return cursor.fetchall()

###############################
#  GET ASYNCHRONOUS RULE IDS  #
###############################
def getAsynchronousRuleIDs( cursor ) :
  cursor.execute( '''SELECT rid FROM Rule WHERE goalTimeArg == "async"''' )
  return cursor.fetchall()

#####################
#  GET SUBGOAL IDS  #
#####################
def getSubgoalIDs( cursor, rid ) :
  cursor.execute( '''SELECT sid FROM Subgoals WHERE rid == "''' + str(rid) + '''"''' )
  return cursor.fetchall()

######################
#  GET SUBGOAL ATTS  #
######################
def getSubgoalAtts( cursor, rid, sid ) :
  cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + str(rid) + "' AND sid == '" + sid + "'" )
  return cursor.fetchall()

#######################
#  REWRITE DEDUCTIVE  #
#######################
def rewriteDeductive( cursor ) :
  timeAtt = "Time"

  # grab all existing non-next and non-async rule ids
  deductiveRuleIDs = getDeductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = clean( deductiveRuleIDs )

  # add attribute 'Time' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()
    newAttID = int(rawMaxID[0] + 1)
    cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "')")

  # add attribute 'Time' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = clean(sids)

    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

  # check for bugs
  if DEDALUSREWRITER_DEBUG :
    print "Rule :"
    cursor.execute('''SELECT * FROM Rule''')
    for i in cursor.fetchall() :
      print i
    
    print "GoalAtt"
    cursor.execute("SELECT * FROM GoalAtt")
    for s in cursor.fetchall():
      print s

    print "Subgoals"
    cursor.execute("SELECT * FROM Subgoals")
    for s in cursor.fetchall():
      print s

    print "SubgoalAtt"
    cursor.execute("SELECT * FROM SubgoalAtt")
    for s in cursor.fetchall():
      print s

  return None

#######################
#  REWRITE INDUCTIVE  #
#######################
def rewriteInductive( cursor ) :
  timeAtt = "SndTime"

  # grab all existing next rule ids
  inductiveRuleIDs = getInductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = clean( inductiveRuleIDs )

  # add attribute 'SndTime+1' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()
    newAttID = int(rawMaxID[0] + 1)
    cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "+1" + "')")

  # add attribute 'SndTime' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = clean(sids)
  
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

      # get current subgoal att list
      subAtts = getSubgoalAtts( cursor, rid, s )

      # get first subgoal att, assume specifies 'sender' node
      firstAtt = subAtts[0]
      firstAtt = firstAtt[0].encode('utf-8')
      #print firstAtt

      # --------------------------------------------------------------------- #

      # add clock subgoal
      # clock(Node, Node, SndTime)
      subgoalName    = "clock"
      subgoalAttList = [ firstAtt, firstAtt, timeAtt ]
      subgoalTimeArg = ""
      subgoalAddArgs = [ "" ]

      # generate random ID for subgoal
      sid = tools.getID()

      # save name and time arg
      cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

      # save subgoal attributes
      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0]) + 1
      for attName in subgoalAttList :
        print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
        cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
        newAttID += 1

      # save subgoal additional args
      for addArg in subgoalAddArgs :
        cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

      # --------------------------------------------------------------------- #

  # check for bugs
  if DEDALUSREWRITER_DEBUG :
    print "Dump all rules : "
    ruleDump( cursor )

  return None

##########################
#  REWRITE ASYNCHRONOUS  #
##########################
def rewriteAsynchronous( cursor ) :
  timeAtt = "SndTime"

  # grab all existing next rule ids
  asynchronousRuleIDs = getAsynchronousRuleIDs( cursor )

  # clean ids
  cleanRIDs = clean( asynchronousRuleIDs )

  # add attribute 'SndTime+1' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()
    newAttID = int(rawMaxID[0] + 1)
    cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "+1" + "')")

  # add attribute 'SndTime' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = clean(sids)
  
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

      # get current subgoal att list
      subAtts = getSubgoalAtts( cursor, rid, s )

      # get first subgoal att, assume specifies 'sender' node
      firstAtt = subAtts[0]
      firstAtt = firstAtt[0].encode('utf-8')
      secondAtt = subAtts[1]
      secondAtt = secondAtt[0].encode('utf-8')
      #print firstAtt

      goalAtts = cursor.execute( "SELECT attName FROM GoalAtt WHERE rid == '" + rid + "'" )
      goalAtts = clean(goalAtts)

      # stop adding a clock relation for every premise
      #if not secondAtt == goalAtts[0] :
      #  break

      # --------------------------------------------------------------------- #

      # add clock subgoal
      # clock(Node, Node, SndTime)
      subgoalName    = "clock"
      subgoalAttList = [ firstAtt, secondAtt, timeAtt ]
      subgoalTimeArg = ""
      subgoalAddArgs = [ "" ]

      # generate random ID for subgoal
      sid = tools.getID()

      # save name and time arg
      cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

      # save subgoal attributes
      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0]) + 1
      for attName in subgoalAttList :
        print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
        cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
        newAttID += 1

      # save subgoal additional args
      for addArg in subgoalAddArgs :
        cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

      # --------------------------------------------------------------------- #

  # check for bugs
  if DEDALUSREWRITER_DEBUG :
    print "Dump all rules : "
    ruleDump( cursor )

  return None

#####################
#  DEDALUS REWRITE  #
#####################
def rewriteDedalus( cursor ) :

  # rewrite deductive rules (aka rules with no time arg)
  rewriteDeductive( cursor )

  # rewrite inductive rules (aka next rules)
  rewriteInductive( cursor )

  # rewrite asynchronous rules (aka async rules)
  rewriteAsynchronous( cursor )

  return None

#########
#  EOF  #
#########
