#!/usr/bin/env python

'''
dumpers.py
   Methods for dumping specific contents from the database.
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
DUMPERS_PYDATALOG_DEBUG = False


################################
#  DUMP SINGLE FACT PYDATALOG  #
################################
# input fid and IR db cursor
# output a single fact in pydatalog notation

def dumpSingleFact_pydatalog( fid, cursor ) :
  fact = ""

  cursor.execute( "SELECT name FROM Fact WHERE fid == '" + fid + "'" ) # get fact name
  factName    = cursor.fetchone()
  factName    = tools.toAscii_str( factName )

  # get list of attribs in fact
  factList    = cursor.execute( "SELECT attName FROM FactAtt WHERE fid == '" + fid + "'" ) # list of fact atts
  factList    = tools.toAscii_list( factList )

  # get fact time arg
  factTimeArg = ""
  cursor.execute( "SELECT timeArg FROM Fact WHERE fid == '" + fid + "'" )
  factTimeArg = cursor.fetchone()
  factTimeArg = tools.toAscii_str( factTimeArg )

  # convert fact info to pretty string
  fact += "pyDatalog.assert_fact('" + factName + "',"
  for j in range(0,len(factList)) :
    if j < (len(factList) - 1) :
      fact += factList[j] + ","
    else :
      fact += factList[j]
  if not factTimeArg == "" :
    fact += "," + factTimeArg
  fact += ")\n"

  return fact

################
#  DUMP CLOCK  #
################
# input IR db cursor
# output all clock facts in pydatalog format

def dumpClock_pydatalog( cursor ) :
  clockFacts = []

  cursor.execute( "SELECT src, dest, sndTime, delivTime FROM Clock" )
  clockFacts = cursor.fetchall()
  clockFacts = tools.toAscii_multiList( clockFacts )

  formattedClockFacts = []
  # convert clock facts to pretty strings
  for fact in clockFacts :
    newFact = "pyDatalog.assert_fact('clock',"

    for i in range(0,len(fact)) :
      if i < (len(fact) - 1) :
        newFact += "'" + fact[i] + "'" + ","
      else :
        newFact += "'" + fact[i] + "'"

    newFact += ")\n"
    formattedClockFacts.append( newFact )

  return formattedClockFacts

################################
#  DUMP SINGLE RULE PYDATALOG  #
################################
# input rid and IR db cursor
# output a single rule

def dumpSingleRule_pydatalog( rid, cursor ) :

  rule = ""

  # -------------------------------------------------------------- #
  #                           GOAL                                 #

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

  # convert goal info to pretty string
  rule += goalName + "("
  for j in range(0,len(goalList)) :
    if j < (len(goalList) - 1) :
      rule += goalList[j] + ","
    else :
      rule += goalList[j] + ")"
  if not goalTimeArg == "" :
    #rule += "@" + goalTimeArg + " <= "
    sys.exit( "ERROR: leftover timeArg in goal: " + rule + "@" + goalTimeArg )
  else :
    rule = "(" + rule + ")"
    rule += " <= "

  # --------------------------------------------------------------- #
  #                         SUBGOALS                                #

  # get list of sids for the subgoals of this rule
  cursor.execute( "SELECT sid FROM Subgoals WHERE rid == '" + str(rid) + "'" ) # get list of sids for this rule
  subIDs = cursor.fetchall()
  subIDs = tools.toAscii_list( subIDs )

  # iterate over subgoal ids
  for k in range(0,len(subIDs)) :
    newSubgoal = "("
    s = subIDs[k]

    # get subgoal name
    cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + str(rid) + "' AND sid == '" + str(s) + "'" )
    subgoalName = cursor.fetchone()

    if not subgoalName == None :
      subgoalName = tools.toAscii_str( subgoalName )

      if DUMPERS_PYDATALOG_DEBUG :
        print "subgoalName = " + subgoalName

      # get subgoal attribute list
      subAtts = cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + rid + "' AND sid == '" + s + "'" )
      subAtts = tools.toAscii_list( subAtts )

      # get subgoal time arg
      cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + rid + "' AND sid == '" + s + "'" ) # get list of sids for this rule
      subTimeArg = cursor.fetchone() # assume only one additional arg
      subTimeArg = tools.toAscii_str( subTimeArg )

      # get subgoal additional args
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + rid + "' AND sid == '" + s + "'" ) # get list of sids for this rule
      subAddArg = cursor.fetchone() # assume only one additional arg
      if not subAddArg == None :
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
        newSubgoal += ") & "

    # notin conversion
    if "notin" in newSubgoal :
      newSubgoal  = newSubgoal.replace( "notin ", "~(" )
      if "&" in newSubgoal :
        newSubgoal = newSubgoal.replace( "&", ")&" )
      else :
        newSubgoal += ")"

    if not k < len( subIDs ) - 1 :
      newSubgoal += ")"

    rule += newSubgoal

  # --------------------------------------------------------------- #
  #                         EQUATIONS                               #

  # get list of sids for the subgoals of this rule
  cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
  eqnIDs = cursor.fetchall()
  eqnIDs = tools.toAscii_list( eqnIDs )

  for e in range(0,len(eqnIDs)) :
    currEqnID = eqnIDs[e]
   
    # get associated equation
    if not currEqnID == None :
      cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + rid + "' AND eid == '" + str(currEqnID) + "'" )
      eqn = cursor.fetchone()
      if not eqn == None :
        eqn = tools.toAscii_str( eqn )

        # convert eqn info to pretty string
        rule += " & (" + str(eqn) + ")"

  # --------------------------------------------------------------- #

  if ",_," in rule :
    rule = rule.replace( ",_,", ",THISISAWILDCARD," )
  if ",_)" in rule :
    rule = rule.replace( ",_)", ",THISISAWILDCARD)" )
  if "(_," in rule :
    rule = rule.replace( "(_,", "(THISISAWILDCARD," )

  rule += "\n" # end all rules with a newline

  return rule


#########
#  EOF  #
######### 
