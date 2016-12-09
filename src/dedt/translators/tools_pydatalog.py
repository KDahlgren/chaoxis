#!/usr/bin/env python

'''
pydatalog_translator.py
   Tools for producig pydatalog programs from the IR in the dedt compiler.
'''

import os, string, sqlite3, sys
import dumpers_pydatalog

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../.." )
sys.path.append( packagePath )

from utils import extractors, tools
# ------------------------------------------------------ #

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from dedt import dedalusParser
# ------------------------------------------------------ #


#############
#  GLOBALS  #
#############
TOOLS_PYDATALOG_DEBUG = True

operators = [ "+", "-", "*", "/", "<", ">", "<=", ">=" ]

##################
#  CHECK FOR OP  #
##################
def checkForOp( myString ) :
  flag = False
  for op in operators :
    if op in myString :
      flag = True
  return flag


####################
#  CLEAN THIS ATT  #
####################
# assumes atts with ops are of the form "ATTNAME<op><integer/float>"
def cleanThisAtt( att ) :
  foundOp = ""
  for op in operators :
    if op in att :
      foundOp = op

  parsedAtt = att.split( foundOp )

  print "att       = "  + att
  print "parsedAtt = " + str(parsedAtt)
  return [parsedAtt[0], parsedAtt[1]]


################
#  SPLIT RULE  #
################
# assumes a properly formed pydatalog rule
def splitRule( rule ) :
  head             = None
  body             = None
  pastAClosedParen = False
  for i in range(0,len(rule)) :
    currChar = rule[i]
    if i < len(rule)-1 :
      nextChar = rule[i+1]

    if currChar == ")" :
      pastAClosedParen = True
    elif pastAClosedParen and (currChar == "<") :
      if nextChar == "=" :
        head = rule[:i-1]
        body = rule[i+2:]

  return [head, body]


##################
#  CONVERT GOAL  #
##################
# kind of hacky
# adds quotes around the atts in the goal att list
#   so the result can be parsed by the dedalus parser.
def parseGoal( rawPydatalogGoal ) :

  goalName    = ""
  goalAttList = []

  afterOpenParen = False
  attList        = ""
  for i in range(0,len(rawPydatalogGoal)) :
    currChar = rawPydatalogGoal[i]
    if currChar == "(" :
      afterOpenParen = True
    if not afterOpenParen :
      goalName += currChar
    else :
      if ( not currChar == "(" ) and ( not currChar == ")" ) :
        attList += currChar

  goalAttList = attList.split(",")

  parsedGoal = [ goalName, "(" ]
  parsedGoal.extend( goalAttList )
  parsedGoal.append( ")" )

  print "rawPydatalogGoal = " + rawPydatalogGoal
  print "attList          = " + str(attList)
  print "parsedGoal       = " + str(parsedGoal)

  return [ parsedGoal, goalName, goalAttList ]


##############
#  GET GOAL  #
##############
def getGoal( rawRule ) :

  print "rawRule = " + str(rawRule)
  splitR  = splitRule( rawRule )
  rawGoal = splitR[0]

  cleanGoal   = parseGoal( rawGoal )
  goalName    = cleanGoal[1]
  goalAttList = cleanGoal[2]

  print "cleanGoal = " + str(cleanGoal)
  return [ cleanGoal, goalName, goalAttList ]


###################
#  GET NEW RULES  #
###################
# input a raw rule in which one of the goal attributes contains a "+" op
# output a list of rules to run the rule in pydatalog 
def getNewRules( rule ) :
  goal     = getGoal( rule )
  goalName = goal[1]
  goalAtts = goal[2]

  if TOOLS_PYDATALOG_DEBUG :
    print "rule = " + str(rule)

  splitR  = splitRule( rule )
  rawBody = splitR[1]

  cleanAtts = []
  opLoc     = 0
  var       = None
  num       = None

  if TOOLS_PYDATALOG_DEBUG :
    print "goalAtts = " + str(goalAtts)

  op = ""
  for i in range(0,len(goalAtts)) :
    att = goalAtts[i]
    if checkForOp( att ) :
      opLoc     = i
      for c in att :
        for o in operators :
          if c == o :
            op = o
      parsedAtt = cleanThisAtt( att )
      var       = parsedAtt[0]
      num       = parsedAtt[1] # assume of the form "VARNAME<op><integer/float>"
      cleanAtts.append( var )
    else :
      cleanAtts.append( att )

  # RULE1 : execute the rule body without imposing the goal op
  tempName1 = "TEMPRELATION" + tools.getID()
  tempRel1  = tempName1 + "(" + ",".join( cleanAtts ) + ")"
  rule1     = tempRel1 + "<=" + rawBody

  # RULE2 : combine the body execution (kind of morbid? >_>) with the result of a function 
  #         executing the desired operation
  rel2Atts        = cleanAtts
  opAtt           = cleanAtts[opLoc]
  rel2Atts[opLoc] = "OPLOC"
  tempName2       = "TEMPRELATION" + tools.getID()
  tempRel2        = tempName2 + "(" + ",".join( rel2Atts ) + ")"
  rule2_1         = tempRel2 + "<=" + tempRel1 + "&"

  print "op = " + op

  if op == "+" :
    rule2_2       = "(OPLOC==(lambda " + opAtt + ": " + opAtt + "+" + num + "))" 
  elif op == "-" :
    rule2_2       = "(OPLOC==(lambda " + opAtt + ": " + opAtt + "-" + num + "))" 
  elif op == "*" :
    rule2_2       = "(OPLOC==(lambda " + opAtt + ": " + opAtt + "*" + num + "))" 
  elif op == "/" :
    rule2_2       = "(OPLOC==(lambda " + opAtt + ": " + opAtt + "/" + num + "))" 
  else :
    sys.exit( "processing non-op rule:\n     " + rule )

  rule2 = rule2_1 + rule2_2

  # RULE 3 : reset the original goal relation name to the second temp view
  rule3 = str(goalName) + "=" + tempName2

  # NEW CREATE_TERMS
  createTerm0 = "pyDatalog.create_terms('OPLOC')\n"
  createTerm1 = "pyDatalog.create_terms('" + tempName1 + "," + tempName2 + "')\n"

  return [createTerm0, createTerm1, rule1, rule2+"\n", rule3+"\n"]


#############
#  OPRULES  #
#############
# input a formatted rule string in which 
#    one of the goal attributes contains an operator.
# output the set of rules necessary to support the 
#    original rule in a pydatalog program.
#
# 1) execute body and store in a temporary view.
# 2) Use the temporary view to populate another temp
#      relation containing specifying the correct op-based
#      attribute(s).
# 3) Write a rule equating the original goal name with the 
#      second temporary view.

# temporary: assume only one attribute with operation per goal.
def opRules( rule ) :
  if TOOLS_PYDATALOG_DEBUG :
    print "... in opRules ..."

  newRules = []

  goal     = getGoal( rule )
  goalAtts = goal[2]

  flag = False
  for att in goalAtts :
    for op in operators :
      if op in att :
        flag = True

  if flag :
    newRules.extend( getNewRules( rule ) )

  if TOOLS_PYDATALOG_DEBUG :
    print "orig rule = " + rule
    print "newRules  = " + str(newRules)

  return newRules

#########
#  EOF  #
#########
