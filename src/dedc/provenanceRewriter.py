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
PROVENANCEREWRITE_DEBUG = True
aggOps = [ "min", "max", "sum", "avg", "count" ] # TODO: make this configurable

##############
#  AGG PROV  #
##############
def aggProv( aggRule, cursor ) :
  bingingsRule = Rule.Rule( cursor )
  firingsRule  = Rule.Rule( cursor )

  # goal name
  # subgoal list info
  # save rule

#######################
#  REGULAR RULE PROV  #
#######################
def regProv( regRule, cursor ) :

  # parse rule
  print "regRule.display() = " + regRule.display()
  parsedRule = dedalusParser.parse( regRule.display() )
  print "parsedRule        = " + str(parsedRule) 

  # generate random ID for new rule
  rid = tools.getID()

  # initialize new rule
  firingsRule = Rule.Rule( rid, cursor )

  # -------------------------------------------------- #

  # get goal info
  goalName    = regRule.getGoalName() + "_firings"
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


########################
#  REWRITE PROVENANCE  #
########################
def rewriteProvenance( ruleMeta, cursor ) :

  # iterate over rules
  for rule in ruleMeta :
    containsAgg = False

    goalAtts = rule.getGoalAttList()

    for agg in aggOps :
      if agg in goalAtts :
        containsAgg = True

    if containsAgg :
      aggProv( rule, cursor )
    else :
      regProv( rule, cursor )

#########
#  EOF  #
#########
