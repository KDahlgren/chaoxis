#!/usr/bin/env python

'''
provenanceRewriter.py
   Define the functionality for adding provenance rules
   to the datalog program.
'''

import inspect, os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import extractors, tools
import dedalusParser
import Rule
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
PROVENANCEREWRITE_DEBUG = False
aggOps = [ "min", "max", "sum", "avg", "count" ] # TODO: make this configurable

timeAtt = "SndTime"

##############
#  AGG PROV  #
##############
def aggProv( aggRule, nameAppend, cursor ) :

  # create bindings rule (see LDFI paper section 4.1.2)
  bindingsRule = regProv( aggRule, nameAppend, cursor )

  # generate random ID
  rid = tools.getID()

  # initialize firings rule
  firingsRule  = Rule.Rule( rid, cursor )

  # goal info
  goalName      = aggRule.getGoalName() + "_prov" + str(rid) # allows tables for duplicate names
  goalAttList   = aggRule.getGoalAttList()
  goalTimeArg   = ""
  rewrittenFlag = 0 # new rules have not yet been rewritten

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "aggProv: goalName    = " + goalName
    print "aggProv: goalAttList = " + str(goalAttList)

  # subgoal list info
  subgoalName         = bindingsRule.getGoalName()
  subgoalAttList_init = bindingsRule.getGoalAttList()

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "aggProv: subgoalName         = " + subgoalName
    print "aggProv: subgoalAttList_init = " + str(subgoalAttList_init)

  aggAtts = []
  for att in goalAttList :
    containsAgg = False
    for op in aggOps :
      if op in att :
        containsAgg = True
    if containsAgg :
      att = att.split("<")
      att = att[1].replace(">", "")
      aggAtts.append( att )

  subgoalAttList_final = []
  for att in subgoalAttList_init :
    for a in aggAtts :
      if a == att:
        subgoalAttList_final.append( "_" )
      else :
        subgoalAttList_final.append( att )

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "aggProv: subgoalAttList_final = " + str(subgoalAttList_final)

  sid = tools.getID()
  subgoalTimeArg = ""
  subgoalAddArgs = ""

  # save rule
  firingsRule.setGoalInfo(               goalName, goalTimeArg, rewrittenFlag  )
  firingsRule.setGoalAttList(            goalAttList                           )
  firingsRule.setSingleSubgoalInfo(      sid, subgoalName, subgoalTimeArg      )
  firingsRule.setSingleSubgoalAttList(   sid, subgoalAttList_final             )
  firingsRule.setSingleSubgoalAddArgs(   sid, subgoalAddArgs                   )


#######################
#  REGULAR RULE PROV  #
#######################
def regProv( regRule, nameAppend, cursor ) :

  if PROVENANCEREWRITE_DEBUG :
    print " ... running regProv ..."

  #sys.exit( "BREAKPOINT: regRule = " + str(regRule.getSubgoalListStr()) )

  # parse rule
  parsedRule = dedalusParser.parse( regRule.display() )

  #sys.exit( "BREAKPOINT: regRule.display() = " + str( regRule.display() ) + "\nparsedRule = " + str(parsedRule) )

  # generate random ID for new rule
  rid = tools.getID()

  # initialize new rule
  firingsRule = Rule.Rule( rid, cursor )

  # -------------------------------------------------- #

  # get goal info
  goalName      = regRule.getGoalName() + nameAppend + str(rid)
  goalTimeArg   = ""
  rewrittenFlag = 1  # new log rules are not rewritten

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "regProv: goalName     = " + goalName

  # -------------------------------------------------- #

  # get subgoal array
  subgoalArray = extractors.extractSubgoalList( parsedRule[1] )

  # ................................... #
  #if goalName.startswith( "pre_prov" ) :
  #  tools.bp( __name__, inspect.stack()[0][3], "subgoalArray = " + str(subgoalArray) )
  # ................................... #

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "regProv: subgoalArray = " + str(subgoalArray)

  # collect goal args while inserting subgoals
  firstSubgoalAtts = []
  goalAttList = []

  # populate with original goal atts first
  goalAttList = regRule.getGoalAttList()

  if PROVENANCEREWRITE_DEBUG :
    print ">>>>>>>> goalAttList init = " + str(goalAttList)

  # then populate with remaining subgoal atts
  for subgoal in subgoalArray :
    # generate random ID for subgoal
    sid = tools.getID()

    # extract info
    subgoalName    = extractors.extractSubgoalName(     subgoal )
    subgoalAttList = extractors.extractAttList(         subgoal ) # returns list
    subgoalTimeArg = ""
    subgoalAddArgs = extractors.extractAdditionalArgs(  subgoal ) # returns list 

    # check for bugs
    if PROVENANCEREWRITE_DEBUG :
      print "regProv: subgoal        = " + str(subgoal)
      print "regProv: subgoalName    = " + subgoalName
      print "regProv: subgoalAttList = " + str(subgoalAttList)
      print "regProv: subgoalAddArgs = " + str(subgoalAddArgs)

    # catch first subgoal att
    if len(subgoalAddArgs) == 0 :
      firstSubgoalAtts.append( subgoalAttList[0] )

    # populate goal attribute list
    for att in subgoalAttList :
      if (not att in goalAttList) and (not att.isdigit()) and (not att == "_") :  # exclude numbers from goal atts
        goalAttList.append( att )

    # make sure time attribute appears as rightmost attribute
    if not goalAttList == None :
      if PROVENANCEREWRITE_DEBUG :
        print "timeAtt = " + timeAtt
        print "old goalAttList = " + str(goalAttList)
      goalAttList = [x for x in goalAttList if x != timeAtt]
      if PROVENANCEREWRITE_DEBUG :
        print "new goalAttList = " + str(goalAttList)
      goalAttList.append(timeAtt)

    # save firings subgoal
    firingsRule.setSingleSubgoalInfo( sid, subgoalName, subgoalTimeArg )
    firingsRule.setSingleSubgoalAttList( sid, subgoalAttList )
    firingsRule.setSingleSubgoalAddArgs( sid, subgoalAddArgs )

  if PROVENANCEREWRITE_DEBUG :
    print ">>>>>>>> goalAttList final = " + str(goalAttList)

  # -------------------------------------------------- #

  # get eqn array
  eqnArray = regRule.getEquationListArray()

  # save firings rule equations
  for eqn in eqnArray :
    # generate random ID
    eid = tools.getID()

    # save eqn
    firingsRule.setSingleEqn( eid, eqn )

  # -------------------------------------------------- #

  # save firings rule goal
  firingsRule.setGoalInfo(     goalName, goalTimeArg, rewrittenFlag  )
  firingsRule.setGoalAttList(  goalAttList                           )

  #sys.exit( "BREAKPOINT: firingsRule = " + str(firingsRule.display()) )
  return firingsRule


########################
#  REWRITE PROVENANCE  #
########################
def rewriteProvenance( ruleMeta, cursor ) :

  if PROVENANCEREWRITE_DEBUG :
    print " ... running rewriteProvenance ... "

  # iterate over rules
  for rule in ruleMeta :
    containsAgg = False

    goalAtts = rule.getGoalAttList()

    for att in goalAtts :
      for agg in aggOps :
        if agg in att :
          containsAgg = True

    if containsAgg :
      aggProv( rule, "_bindings", cursor )
    else :
      regProv( rule, "_prov", cursor )

  if PROVENANCEREWRITE_DEBUG :
    print " ... done rewriteProvenance ... "

#########
#  EOF  #
#########
