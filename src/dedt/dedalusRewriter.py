#!/usr/bin/env python

'''
dedalusRewriter.py
   Define the functionality for rewriting Dedalus into datalog.
'''

import inspect, os, sys

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

timeAtt_snd    = "SndTime"
timeAtt_deliv  = "DelivTime"
rewrittenFlag  = "True"

############################
#  GET DEDUCTIVE RULE IDS  #
############################
def getDeductiveRuleIDs( cursor ) :
  # deductive rules are not next or async
  cursor.execute( "SELECT rid FROM Rule WHERE (NOT goalTimeArg == 'next') AND (NOT goalTimeArg == 'async')" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )
  return ridList

############################
#  GET INDUCTIVE RULE IDS  #
############################
def getInductiveRuleIDs( cursor ) :
  cursor.execute( "SELECT rid FROM Rule WHERE goalTimeArg == 'next'" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )
  return ridList

###############################
#  GET ASYNCHRONOUS RULE IDS  #
###############################
def getAsynchronousRuleIDs( cursor ) :
  cursor.execute( "SELECT rid FROM Rule WHERE goalTimeArg == 'async'" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )
  return ridList

#####################
#  GET SUBGOAL IDS  #
#####################
def getSubgoalIDs( cursor, rid ) :
  cursor.execute( "SELECT sid FROM Subgoals WHERE rid == '" + str(rid) + "'" )
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

  # add attribute 'SndTime' to head as the new rightmost attribute
  for rid in deductiveRuleIDs :

    # ......................................... #
    cursor.execute( "SELECT goalName FROM Rule WHERE rid =='" + rid + "'" )
    goalName = cursor.fetchone()
    goalName = tools.toAscii_str( goalName )
    # ......................................... #

    #print "*******************************"
    #print "old rule : " + str( dumpers.reconstructRule(rid, cursor) )

    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + rewrittenFlag + "' WHERE rid=='" + rid + "'" )

      # grab maximum attribute id
      cursor.execute( "SELECT MAX(attID) FROM GoalAtt WHERE rid == '" + rid + "'" )
      rawMaxID = cursor.fetchone()
      rawMaxID = rawMaxID[0] # extract from tuple

      if rawMaxID or (rawMaxID == 0) :
        newAttID = int(rawMaxID + 1) # the att id for SndTime

        # check if add arg is a specific time
        cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + rid + "'" )
        timeArg = cursor.fetchone()
        timeArg = tools.toAscii_str( timeArg )

        if timeArg.isdigit() :
          cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeArg + "','int')")
        else :
          cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_snd + "','int')")

      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : current rule goal has no attributes:\n" + dumpers.reconstructRule( rid, cursor ) )

      # add attribute 'Time' to all subgoals
      sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
      sids = tools.toAscii_list(sids)

      firstSubgoalAtts = []
      # iterate over rule subgoals
      for s in sids :

        # ......................................... #
        cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + rid + "' AND sid=='" + s + "'" )
        subgoalName = cursor.fetchone()
        subgoalName = tools.toAscii_str( subgoalName )
        # ......................................... #

        addArg = None

        # get time arg for subgoal
        cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid = '" + rid + "' AND sid = '" + s + "'" )
        timeArg = cursor.fetchone()
        timeArg = tools.toAscii_str( timeArg )

        # add Time as a subgoal attribute
        cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
        rawMaxID = cursor.fetchone() # int type
        newAttID = int(rawMaxID[0] + 1)
        cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "'," + str(newAttID) + ",'" + timeAtt_snd + "','int')")

        # replace subgoal time attribute with numeric time arg
        if timeArg.isdigit() :
          cursor.execute( "SELECT attName FROM SubgoalAtt WHERE sid = '" + s + "'" )
          satts = cursor.fetchall()
          satts = tools.toAscii_list( satts )

          # ......................................... #
          #if goalName == "pre" :
          #  if subgoalName == "bcast" :
          #    print " timeArg = " + str(timeArg)
          #    print " satts   = " + str(satts)
          #    tools.bp( __name__, inspect.stack()[0][3], "___ASDFASLKDHFWER" )
          # ......................................... #

          for i in range(0,len(satts)) :
            if satts[i] == timeAtt_snd :
              cursor.execute( "UPDATE SubgoalAtt SET attName='" + timeArg + "' WHERE rid = '" + rid + "' AND sid = '" + s + "' AND attID = '" + str(i) + "'")

        # collect the additional argument (aka notin for c4)
        cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE SubgoalAddArgs.rid == '" + rid + "' AND SubgoalAddArgs.sid == '" + s + "'"  )
        addArg = cursor.fetchone()
        if addArg :
          addArg = tools.toAscii_str( addArg )

        # while we're here, collect the first attribute of this subgoal
        cursor.execute("SELECT attName FROM SubgoalAtt WHERE SubgoalAtt.sid == '" + s + "' AND SubgoalAtt.attID == '" + str(0) + "'")
        firstAtt = cursor.fetchone()
        if (not firstAtt == None) and (not addArg == "notin") :
          firstAtt = tools.toAscii_str( firstAtt )
          firstSubgoalAtts.append( firstAtt )
        else :
          if DEDALUSREWRITER_DEBUG :
            print "firstAtt = " + str(firstAtt)

      # sanity checking branch
      if len( firstSubgoalAtts ) > 0 :
        # add clock subgoal
        clockTools.addClockSubgoal_deductive( rid, firstSubgoalAtts, timeAtt_snd, timeAtt_deliv, cursor )
      else :
        print dumpers.reconstructRule( rid, cursor )
        tools.bp( __name__, inspect.stack()[0][3], "You've got major probs, mate. The subgoals of this rule have no attributes.\nfirstSubgoalAtts = " + str(firstSubgoalAtts) )

    #tools.bp( __name__, inspect.stack()[0][3], "new rule : " + str(dumpers.reconstructRule(rid, cursor)) )

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

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "inductiveRuleIDs = " + str(inductiveRuleIDs)
    print "<><><><><><><><><><><><><><><>"
    print "    DUMPING INDUCTIVE RULES   "
    for r in inductiveRuleIDs :
      print dumpers.reconstructRule( r, cursor )
    print "<><><><><><><><><><><><><><><>"

  # add attribute 'SndTime+1' to head
  for rid in inductiveRuleIDs :

    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + rewrittenFlag + "' WHERE rid=='" + rid + "'" )

      # grab maximum attribute id
      cursor.execute( "SELECT MAX(attID) FROM GoalAtt WHERE rid == '" + rid + "'" )
      rawMaxID = cursor.fetchone()
      rawMaxID = rawMaxID[0] # extract from tuple

      # .................................. #
      #cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + rid + "'" )
      #goalName = cursor.fetchone()
      #goalName = tools.toAscii_str( goalName )
      #print "___ goalName = " + str(goalName)
      #if goalName == "clients" :
      #  print "rawMaxID = " + str( rawMaxID )
      #  sys.exit()
      # .................................. #

      if rawMaxID or (rawMaxID == 0) :
        newAttID = int(rawMaxID + 1) # the att id for SndTime

        # check if add arg is a specific time
        cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + rid + "'" )
        timeArg = cursor.fetchone()
        timeArg = tools.toAscii_str( timeArg )

        # add attribute 'SndTime+1' to head
        cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_snd + "+1" + "','int')")
      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : current rule goal has no attributes:\n" + dumpers.reconstructRule( rid, cursor ) )

      if DEDALUSREWRITER_DEBUG :
        print "inductive: rawMaxID    = " + str(rawMaxID)
        print "inductive: rawMaxID[0] = " + str(rawMaxID[0])

  #   add attribute 'SndTime' to all subgoals
  for rid in inductiveRuleIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)

    firstSubgoalAtts = [] 
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "'," + str(newAttID) + ",'" + timeAtt_snd + "','int')")

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
  for rid in inductiveRuleIDs :
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

  # check for bugs
  if DEDALUSREWRITER_DUMPS_DEBUG :
    print "asynchronousRuleIDs = " + str(asynchronousRuleIDs)
    for r in asynchronousRuleIDs :
      print "<><><><><><><><><><><><><><><>"
      print "    DUMPING ASYNC RULES   "
      print dumpers.reconstructRule( r, cursor )
      print "<><><><><><><><><><><><><><><>"

  # add attribute 'DelivTime' to head
  for rid in asynchronousRuleIDs :

    #print "*******************************"
    #print "old rule : " + str( dumpers.reconstructRule(rid, cursor) )

    if not tools.checkIfRewrittenAlready( rid, cursor ) :
      # set rule as rewritten 
      cursor.execute( "UPDATE Rule SET rewritten='" + rewrittenFlag + "' WHERE rid=='" + rid + "'" )

      cursor.execute('''SELECT MAX(attID) FROM GoalAtt WHERE GoalAtt.rid == "''' + rid + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(newAttID) + "','" + timeAtt_deliv + "','int')")
  
  # add attribute 'SndTime' to all subgoals and add clock subgoal
  for rid in asynchronousRuleIDs :
    sids = getSubgoalIDs( cursor, rid ) # get all subgoal ids
    sids = tools.toAscii_list(sids)
  
    firstSubgoalAtts = []
    for s in sids :
      cursor.execute('''SELECT MAX(attID) FROM SubgoalAtt WHERE SubgoalAtt.sid == "''' + s + '''"''')
      rawMaxID = cursor.fetchone()
      newAttID = int(rawMaxID[0] + 1)
      cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + s + "'," + str(newAttID) + ",'" + timeAtt_snd + "','int')")

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
    for rid in asynchronousRuleIDs :
      cursor.execute( "UPDATE Rule SET goalTimeArg='' WHERE rid='" + rid + "'"  )

    #print "new rule : " + str( dumpers.reconstructRule(rid, cursor) )
    #print "-------------------------------"
    #tools.bp( __name__, inspect.stack()[0][3], "breakhere" )

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
