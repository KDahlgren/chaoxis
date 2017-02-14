#!/usr/bin/env python

'''
clockTools.py
  methods for adding clock subgoals to different rule types.
'''

import os, random, re, string, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

import dumpers, tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
CLOCKTOOLS_DEBUG = False


#################################
#  ADD CLOCK SUBGOAL DEDUCTIVE  #
#################################
# input the list of attributes form the first subgoal in the rule, IR db cursor
# output nothing, modified IR DB
def addClockSubgoal_deductive( rid, firstSubgoalAtts, timeAtt_snd, timeAtt_deliv, cursor ) :
  baseAtt = firstSubgoalAtts[0]

  if CLOCKTOOLS_DEBUG :
    print "CLOCKTOOLS_DEBUG: For rule : " + str( dumpers.reconstructRule( rid, cursor ) + "\n    firstSubgoalAtts = " + str(firstSubgoalAtts) )

  for c in firstSubgoalAtts :
    if not c == baseAtt :
      sys.exit("Syntax error:\n   Offending rule:\n      " + dumpers.reconstructRule( rid, cursor ) + "\n   The first attribute of all positive subgoals in deductive rules must be identical. Semantically, the first attribute is expected to represent the message sender.\n    First att list for positive subgoals: " + str(firstSubgoalAtts) )

  # get first att in first subgoal, assume specifies 'sender' node
  firstAtt = baseAtt

  # get first att of goal, assume specifies 'reciever' node
  # while we're here, collect the first attribute of this goal
  cursor.execute("SELECT attName FROM GoalAtt WHERE GoalAtt.rid == '" + rid + "' AND GoalAtt.attID == '" + str(0) + "'")
  firstGoalAtt = cursor.fetchone()
  firstGoalAtt = tools.toAscii_str( firstGoalAtt )

  # define second clock attribute
  secondAtt = firstAtt

  # add clock subgoal
  # clock(Node1, Node1, SndTime, DelivTime)
  subgoalName    = "clock"
  #subgoalAttList = [ firstAtt, secondAtt, timeAtt_snd, timeAtt_deliv ]
  subgoalAttList = [ firstAtt, secondAtt, timeAtt_snd, "_" ]
  subgoalTimeArg = ""
  subgoalAddArgs = [ "" ]

  # generate random ID for subgoal
  sid = tools.getID()

  # save name and time arg
  cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

  # save subgoal attributes
  cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
  rawMaxID = cursor.fetchone()
  #newAttID = int(rawMaxID[0]) + 1
  newAttID = 0
  for attName in subgoalAttList :
    if CLOCKTOOLS_DEBUG :
      print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
    cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
    newAttID += 1

  # save subgoal additional args
  for addArg in subgoalAddArgs :
    cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

  # reset variables for next async rule
  firstSubgoalAtts = []
  firstGoalAtt     = ""


#################################
#  ADD CLOCK SUBGOAL INDUCTIVE  #
#################################
# input the list of attributes form the first subgoal in the rule, IR db cursor
# output nothing, modified IR DB
def addClockSubgoal_inductive( rid, firstSubgoalAtts, timeAtt_snd, timeAtt_deliv, cursor ) :
  baseAtt = firstSubgoalAtts[0]

  if CLOCKTOOLS_DEBUG :
    print "CLOCKTOOLS_DEBUG: For rule : " + str( dumpers.reconstructRule( rid, cursor ) + "\n    firstSubgoalAtts = " + str(firstSubgoalAtts) )

  for c in firstSubgoalAtts :
    if not c == baseAtt :
      sys.exit("Syntax error:\n   Offending rule:\n      " + dumpers.reconstructRule( rid, cursor ) + "\n   The first attribute of all positive subgoals in deductive rules must be identical. Semantically, the first attribute is expected to represent the message sender.\n    First att list for positive subgoals: " + str(firstSubgoalAtts) )

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
  #subgoalAttList = [ firstAtt, secondAtt, timeAtt_snd, timeAtt_deliv ]
  subgoalAttList = [ firstAtt, "_", timeAtt_snd, "_" ]
  subgoalTimeArg = ""
  subgoalAddArgs = [ "" ]

  # generate random ID for subgoal
  sid = tools.getID()

  # save name and time arg
  cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

  # save subgoal attributes
  cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
  rawMaxID = cursor.fetchone()
  #newAttID = int(rawMaxID[0]) + 1
  newAttID = 0
  for attName in subgoalAttList :
    if CLOCKTOOLS_DEBUG :
      print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
    cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
    newAttID += 1

  # save subgoal additional args
  for addArg in subgoalAddArgs :
    cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

  # reset variables for next async rule
  firstSubgoalAtts = []
  firstGoalAtt     = ""

#############################
#  ADD CLOCK SUBGOAL ASYNC  #
#############################
# input the list of attributes form the first subgoal in the rule, IR db cursor
# output nothing, modified IR DB
def addClockSubgoal_async( rid, firstSubgoalAtts, secondAtt, timeAtt_snd, timeAtt_deliv, cursor ) :
  baseAtt = firstSubgoalAtts[0]

  if CLOCKTOOLS_DEBUG :
    print "CLOCKTOOLS_DEBUG: For rule : " + str( dumpers.reconstructRule( rid, cursor ) + "\n    firstSubgoalAtts = " + str(firstSubgoalAtts) )

  for c in firstSubgoalAtts :
    if not c == baseAtt :
      sys.exit("Syntax error:\n   Offending rule:\n      " + dumpers.reconstructRule( rid, cursor ) + "\n   The first attribute of all positive subgoals in deductive rules must be identical. Semantically, the first attribute is expected to represent the message sender.\n    First att list for positive subgoals: " + str(firstSubgoalAtts) )

  # get first att in first subgoal, assume specifies 'sender' node
  firstAtt = baseAtt

  # get first att of goal, assume specifies 'reciever' node
  # while we're here, collect the first attribute of this goal
  cursor.execute("SELECT attName FROM GoalAtt WHERE GoalAtt.rid == '" + rid + "' AND GoalAtt.attID == '" + str(0) + "'")
  firstGoalAtt = cursor.fetchone()
  firstGoalAtt = tools.toAscii_str( firstGoalAtt )

  # add clock subgoal
  # clock(Node1, Node2, SndTime)
  subgoalName    = "clock"
  subgoalAttList = [ firstAtt, secondAtt, timeAtt_snd, timeAtt_deliv ]
  subgoalTimeArg = ""
  subgoalAddArgs = [ "" ]

  # generate random ID for subgoal
  sid = tools.getID()

  # save name and time arg
  cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

  # save subgoal attributes
  cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
  rawMaxID = cursor.fetchone()
  #newAttID = int(rawMaxID[0]) + 1
  newAttID = 0
  for attName in subgoalAttList :
    if CLOCKTOOLS_DEBUG :
      print rid, sid, subgoalName, subgoalTimeArg, str(newAttID), attName
    cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(newAttID) + "','" + attName + "')")
    newAttID += 1

  # save subgoal additional args
  for addArg in subgoalAddArgs :
    cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

  # reset variables for next async rule
  firstSubgoalAtts = []
  firstGoalAtt     = ""


#########
#  EOF  #
#########
