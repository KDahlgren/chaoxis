#!/usr/bin/env python

'''
provenanceRewriter.py
   Define the functionality for adding provenance rules
   to the datalog program.
'''

import os, sys

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
  goalName    = aggRule.getGoalName() + "_prov"
  goalAttList = aggRule.getGoalAttList()
  goalTimeArg = aggRule.getGoalTimeArg()

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "aggProv: goalName    = " + goalName
    print "aggProv: goalAttList = " + str(goalAttList)
    print "aggProv: goalTimeArg = " + goalTimeArg

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
  firingsRule.setGoalInfo(               goalName, goalTimeArg            )
  firingsRule.setGoalAttList(            goalAttList                      )
  firingsRule.setSingleSubgoalInfo(      sid, subgoalName, subgoalTimeArg )
  firingsRule.setSingleSubgoalAttList(   sid, subgoalAttList_final        )
  firingsRule.setSingleSubgoalAddArgs(   sid, subgoalAddArgs              )


#######################
#  REGULAR RULE PROV  #
#######################
def regProv( regRule, nameAppend, cursor ) :

  # parse rule
  parsedRule = dedalusParser.parse( regRule.display() )

  # generate random ID for new rule
  rid = tools.getID()

  # initialize new rule
  firingsRule = Rule.Rule( rid, cursor )

  # -------------------------------------------------- #

  # get goal info
  goalName    = regRule.getGoalName() + nameAppend
  goalTimeArg = regRule.getGoalTimeArg()

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "regProv: goalName     = " + goalName
    print "regProv: goalTimeArg  = " + goalTimeArg

  # -------------------------------------------------- #

  # get subgoal array
  subgoalArray = extractors.extractSubgoalList( parsedRule[1] )

  # check for bugs
  if PROVENANCEREWRITE_DEBUG :
    print "regProv: subgoalArray = " + str(subgoalArray)

  # collect goal args while inserting subgoals
  goalAttList = []
  for subgoal in subgoalArray :
    # generate random ID for subgoal
    sid = tools.getID()

    # TODO: create new extraction methods
    subgoalName    = extractors.extractSubgoalName(     subgoal )
    subgoalAttList = extractors.extractAttList(         subgoal ) # returns list
    subgoalTimeArg = extractors.extractTimeArg(         subgoal )
    subgoalAddArgs = extractors.extractAdditionalArgs(  subgoal ) # returns list 

    # check for bugs
    if PROVENANCEREWRITE_DEBUG :
      print "regProv: subgoal        = " + str(subgoal)
      print "regProv: subgoalName    = " + subgoalName
      print "regProv: subgoalAttList = " + str(subgoalAttList)
      print "regProv: subgoalTimeArg = " + subgoalTimeArg
      print "regProv: subgoalAddArgs = " + str(subgoalAddArgs)

    # populate goal attribute list
    for att in subgoalAttList :
      if not att in goalAttList :
        goalAttList.append( att )

    # save firings subgoal
    firingsRule.setSingleSubgoalInfo( sid, subgoalName, subgoalTimeArg )
    firingsRule.setSingleSubgoalAttList( sid, subgoalAttList )
    firingsRule.setSingleSubgoalAddArgs( sid, subgoalAddArgs )

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
  firingsRule.setGoalInfo(     goalName, goalTimeArg )
  firingsRule.setGoalAttList(  goalAttList           )

  return firingsRule

########################
#  REWRITE PROVENANCE  #
########################
def rewriteProvenance( ruleMeta, cursor ) :

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


#########
#  EOF  #
#########
