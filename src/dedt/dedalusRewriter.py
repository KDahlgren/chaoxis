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

from utils import clockTools, tools, dumpers
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDALUSREWRITER_DEBUG       = False
DEDALUSREWRITER_DUMPS_DEBUG = False

timeAtt_snd   = "SndTime"
timeAtt_deliv = "DelivTime"
rewrittenFlag  = 1 

############################
#  GET DEDUCTIVE RULE IDS  #
############################
def getDeductiveRuleIDs( cursor ) :
  cursor.execute( '''SELECT rid FROM Rule WHERE (NOT goalTimeArg == "next") AND (NOT goalTimeArg == "async")''' )
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

  # grab all existing non-next and non-async rule ids
  deductiveRuleIDs = getDeductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( deductiveRuleIDs )

  # add attribute 'SndTime' to head
  for rid in cleanRIDs :
    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + str(rewrittenFlag) + "' WHERE rid='" + rid + "'" )

      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()
      if not rawMaxID[0] == None :
        newAttID = int(rawMaxID[0] + 1)
        # check if add arg is a specific time
        cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + rid + "'" )
        timeArg = cursor.fetchone()
        timeArg = tools.toAscii_str( timeArg )
        if timeArg.isdigit() :
          cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeArg + "')")
        else :
          cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_snd + "')")

      # add attribute 'Time' to all subgoals
      sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
      sids = tools.toAscii_list(sids)

      firstSubgoalAtts = []
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
        cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt_snd + "')")

        # replace subgoal time attribute with numeric time arg
        if timeArg.isdigit() :
          cursor.execute( "SELECT attName FROM SubgoalAtt WHERE sid = '" + s + "'" )
          satts = cursor.fetchall()
          satts = tools.toAscii_list( satts )

          for i in range(0,len(satts)) :
            if satts[i]  == timeAtt_snd :
              cursor.execute( "UPDATE SubgoalAtt SET attName='" + timeArg + "' WHERE rid = '" + rid + "' AND sid = '" + s + "' AND attID = '" + str(i) + "'")

        # while we're here, collect the first attribute of this subgoal
        cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE SubgoalAddArgs.rid == '" + rid + "' AND SubgoalAddArgs.sid == '" + s + "'"  )
        addArg = cursor.fetchone()
        if not addArg == None :
          addArg = tools.toAscii_str( addArg )

        cursor.execute("SELECT attName FROM SubgoalAtt WHERE SubgoalAtt.sid == '" + s + "' AND SubgoalAtt.attID == '" + str(0) + "'")
        firstAtt = cursor.fetchone()
        if (not firstAtt == None) and (not addArg == "notin") :
          firstAtt = tools.toAscii_str( firstAtt )
          firstSubgoalAtts.append( firstAtt )
        else :
          if DEDALUSREWRITER_DEBUG :
            print "firstAtt = " + str(firstAtt)

      # add clock subgoal
      clockTools.addClockSubgoal_deductive( rid, firstSubgoalAtts, timeAtt_snd, timeAtt_deliv, cursor )

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
    print " ... running inductive rewrite ... "

  # grab all existing next rule ids
  inductiveRuleIDs = getInductiveRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( inductiveRuleIDs )

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "cleanRIDs = " + str(cleanRIDs)
    print "<><><><><><><><><><><><><><><>"
    print "    DUMPING INDUCTIVE RULES   "
    for r in cleanRIDs :
      print dumpers.reconstructRule( r, cursor )
    print "<><><><><><><><><><><><><><><>"

  # add attribute 'SndTime+1' to head
  for rid in cleanRIDs :

    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + str(rewrittenFlag) + "' WHERE rid='" + rid + "'" )

      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()

      if DEDALUSREWRITER_DEBUG :
        print "inductive: rawMaxID    = " + str(rawMaxID)
        print "inductive: rawMaxID[0] = " + str(rawMaxID[0])

      if not rawMaxID[0] == None :
        newAttID = int(rawMaxID[0] + 1)
        cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_snd + "+1" + "')")

  #   add attribute 'SndTime' to all subgoals
  for rid in cleanRIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)

    firstSubgoalAtts = [] 
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt_snd + "')")

      # while we're here, collect the first attribute of this subgoal
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE SubgoalAddArgs.rid == '" + rid + "' AND SubgoalAddArgs.sid == '" + s + "'"  )
      addArg = cursor.fetchone()
      if not addArg == None :
        addArg = tools.toAscii_str( addArg )

      cursor.execute("SELECT attName FROM SubgoalAtt WHERE SubgoalAtt.sid == '" + s + "' AND SubgoalAtt.attID == '" + str(0) + "'")
      firstAtt = cursor.fetchone()
      if (not firstAtt == None) and (not addArg == "notin") :
        firstAtt = tools.toAscii_str( firstAtt )
        firstSubgoalAtts.append( firstAtt )
      else :
        if DEDALUSREWRITER_DEBUG :
          print "firstAtt = " + str(firstAtt)

    # add clock subgoal
    clockTools.addClockSubgoal_inductive( rid, firstSubgoalAtts, timeAtt_snd, timeAtt_deliv, cursor )

  # remove time arg from rule goals
  for rid in cleanRIDs :
    cursor.execute( "UPDATE Rule SET goalTimeArg='' WHERE rid='" + rid + "'"  )

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "Dump all rules from inductive : "
    dumpers.ruleDump( cursor )


  if DEDALUSREWRITER_DEBUG :
    print "... done rewriteInductive ..."

  return None

##########################
#  REWRITE ASYNCHRONOUS  #
##########################
def rewriteAsynchronous( cursor ) :

  if DEDALUSREWRITER_DEBUG :
    print " ... running asynchronous rewrite ... "

  # grab all existing next rule ids
  asynchronousRuleIDs = getAsynchronousRuleIDs( cursor )

  # clean ids
  cleanRIDs = tools.toAscii_list( asynchronousRuleIDs )

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "cleanRIDs = " + str(cleanRIDs)
    for r in cleanRIDs :
      print "<><><><><><><><><><><><><><><>"
      print "    DUMPING ASYNC RULES   "
      print dumpers.reconstructRule( r, cursor )
      print "<><><><><><><><><><><><><><><>"

  # add attribute 'DelivTime' to head
  for rid in cleanRIDs :
    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + str(rewrittenFlag) + "' WHERE rid='" + rid + "'" )

      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_deliv + "')")
  
    # add attribute 'SndTime' to all subgoals
    for rid in cleanRIDs :
      sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
      sids = tools.toAscii_list(sids)
    
      firstSubgoalAtts = []
      for s in sids :
        cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
        rawMaxID = cursor.fetchone()
        newAttID = int(rawMaxID[0] + 1)
        cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "','" + str(newAttID) + "','" + timeAtt_snd + "')")
  
        # while we're here, collect the first attribute of this subgoal
        cursor.execute("SELECT attName FROM SubgoalAtt WHERE SubgoalAtt.sid == '" + s + "' AND SubgoalAtt.attID == '" + str(0) + "'")
        firstAtt = cursor.fetchone()
        if firstAtt :
          firstAtt = tools.toAscii_str( firstAtt )
          firstSubgoalAtts.append( firstAtt )
  
  
      # add clock subgoal
      cursor.execute( "SELECT attName FROM GoalAtt WHERE GoalAtt.rid == '" + rid + "' AND GoalAtt.attID == '" + str(0) + "'")
      secondAtt = cursor.fetchone()
      secondAtt = tools.toAscii_str( secondAtt )
      clockTools.addClockSubgoal_async( rid, firstSubgoalAtts, secondAtt, timeAtt_snd, timeAtt_deliv, cursor )
  
    # remove time arg from rule goals
    for rid in cleanRIDs :
      cursor.execute( "UPDATE Rule SET goalTimeArg='' WHERE rid='" + rid + "'"  )
  
    # check for bugs
    if DEDALUSREWRITER_DUMPS_DEBUG :
      print "Dump all rules from async : "
      dumpers.ruleDump( cursor )
      #dumpers.factDump( cursor )

  if DEDALUSREWRITER_DEBUG :
    print " ... done asynchronous rewrite ... "

  return None


#####################
#  DEDALUS REWRITE  #
#####################
def rewriteDedalus( cursor ) :

  if DEDALUSREWRITER_DEBUG :
    print " ... running rewriteDedalus ... "

  # rewrite deductive rules (aka rules with no time arg)
  rewriteDeductive( cursor )

  # rewrite inductive rules (aka next rules)
  rewriteInductive( cursor )

  # rewrite asynchronous rules (aka async rules)
  rewriteAsynchronous( cursor )

  if DEDALUSREWRITER_DEBUG :
    print " ... done rewriteDedalus ... "

  return None

#########
#  EOF  #
#########
