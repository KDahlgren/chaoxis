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

from utils import tools, dumpers
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDALUSREWRITER_DEBUG = False
DEDALUSREWRITER_DUMPS_DEBUG = False

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

  if DEDALUSREWRITER_DEBUG :
    print " ... running deductive rewrite ..."

  timeAtt = "Time"

  # grab all existing non-next and non-async rule ids
  deductiveRuleIDs = getDeductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( deductiveRuleIDs )

  # add attribute 'Time' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()
    if not rawMaxID[0] == None :
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "')")

  # add attribute 'Time' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)

    # iterate over rule subgoals
    for s in sids :
      # get time arg for subgoal
      cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid = '" + rid + "' AND sid = '" + s + "'" )
      timeArg = cursor.fetchone()
      timeArg = tools.toAscii_str( timeArg )

      # add Time as a subgoal attribute
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

      # replace subgoal time attribute with numeric time arg
      if timeArg.isdigit() :
        cursor.execute( "SELECT attName FROM SubgoalAtt WHERE sid = '" + s + "'" )
        satts = cursor.fetchall()
        satts = tools.toAscii_list( satts )

        for i in range(0,len(satts)) :
          if satts[i]  == "Time" :
            cursor.execute( "UPDATE SubgoalAtt SET attName='" + timeArg + "' WHERE rid = '" + rid + "' AND sid = '" + s + "' AND attID = '" + str(i) + "'")

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


#######################
#  REWRITE INDUCTIVE  #
#######################
def rewriteInductive( cursor ) :

  if DEDALUSREWRITER_DEBUG :
    print " ... running inductive rewrite ..."

  timeAtt = "Time"

  # grab all existing next rule ids
  inductiveRuleIDs = getInductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( inductiveRuleIDs )

  # add attribute 'SndTime+1' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()

    if DEDALUSREWRITER_DEBUG :
      print "inductive: rawMaxID    = " + str(rawMaxID)
      print "inductive: rawMaxID[0] = " + str(rawMaxID[0])

    if not rawMaxID[0] == None :
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "+1" + "')")

  # add attribute 'SndTime' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)
  
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

  # remove time arg from rule goals
  for rid in cleanRIDs :
    cursor.execute( "UPDATE Rule SET goalTimeArg='' WHERE rid='" + rid + "'"  )

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "Dump all rules inductive : "
    dumpers.ruleDump( cursor )

  return None

##########################
#  REWRITE ASYNCHRONOUS  #
##########################
def rewriteAsynchronous( cursor ) :
  timeAtt = "SndTime"

  firstSubgoalAtts = []
  firstGoalAtt     = ""

  # grab all existing next rule ids
  asynchronousRuleIDs = getAsynchronousRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( asynchronousRuleIDs )

  # add attribute 'SndTime+1' to head
  for rid in cleanRIDs :
    cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
    rawMaxID = cursor.fetchone()
    newAttID = int(rawMaxID[0] + 1)
    cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt + "+1" + "')")

  # add attribute 'SndTime' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)
  
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt + "')")

      # while we're here, collect the first attribute of this subgoal
      cursor.execute("SELECT attName FROM SubgoalAtt WHERE SubgoalAtt.sid == '" + s + "' AND SubgoalAtt.attID == '" + str(0) + "'")
      firstAtt = cursor.fetchone()
      firstAtt = tools.toAscii_str( firstAtt )
      firstSubgoalAtts.append( firstAtt )

    # --------------------------------------------------------------------- #
    #                       ADD CLOCK RELATION                              #

    # sanity check

    baseAtt = firstSubgoalAtts[0]

    for c in firstSubgoalAtts :
      if not c == baseAtt :
        sys.exit("Syntax error:\n   Offending rule:\n      " + dumpers.reconstructRule( rid, cursor ) + "\n   The first attribute of all subgoals in async rules must be identical. Semantically, the first attribute is expected to represent the message sender." )

    # get first att in first subgoal, assume specifies 'sender' node
    firstAtt = baseAtt

    # get first att of goal, assume specifies 'reciever' node
    # while we're here, collect the first attribute of this goal
    cursor.execute("SELECT attName FROM GoalAtt WHERE GoalAtt.rid == '" + rid + "' AND GoalAtt.attID == '" + str(0) + "'")
    firstGoalAtt = cursor.fetchone()
    firstGoalAtt = tools.toAscii_str( firstGoalAtt )

    # define second clock attribute
    secondAtt = firstGoalAtt

    # add clock subgoal
    # clock(Node1, Node2, SndTime)
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
      if DEDALUSREWRITER_DEBUG :
        print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
      newAttID += 1

    # save subgoal additional args
    for addArg in subgoalAddArgs :
      cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

    # reset variables for next async rule
    firstSubgoalAtts = []
    firstGoalAtt     = ""

    # --------------------------------------------------------------------- #

  # remove time arg from rule goals
  for rid in cleanRIDs :
    cursor.execute( "UPDATE Rule SET goalTimeArg='' WHERE rid='" + rid + "'"  )

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "Dump all rules from async : "
    dumpers.ruleDump( cursor )
    #dumpers.factDump( cursor )

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
