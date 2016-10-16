#!/usr/bin/env python

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import messages, sanityChecks, parseCommandLineInput
from utils.Table import Table
# ------------------------------------------------------ #

######################
#  GET SUBGOAL LIST  #
######################
# input the enitre body string
# output list of subgoals
def getSubgoalList( body ) :
  subgoalList = []

  # iterate over all characters in body, clean up delimiters
  afterAnOpenParen = False
  afterAnAmpersand = False
  for i in range(0,len(body)) :
    # commas delimiting subgoals necessarily do not occur after an open parenthesis
    if body[i] == "(" :
      afterAnOpenParen = True
    elif body[i] == ")" :
      afterAnOpenParen = False
    # commas delimiting subgoals may appear after and integer prepended with an ampersand
    if body[i] == "@" :
      afterAnAmpersand = True
    elif body[i] == ",)" :
      afterAnAmpersand = False

    # relations can have lists of attributes within parentheses (eg choice)
    if (not afterAnOpenParen) and (body[i-1] == ")") and (body[i] == ",") :
      body = body[:i-1] + "--DELIMITHERE--" + body[i:]
    elif (not afterAnOpenParen) and (body[i-1] == ")") and (body[i] == ",") :
      body = body[:i-1] + "--DELIMITHERE--" + body[i:]
    elif afterAnAmpersand and (body[i] == ",") :
      body = body[:i] + "--DELIMITHERE--" + body[i:]

  tmpSubgoalList = body.split( "--DELIMITHERE--" )
  for i in range(0,len(tmpSubgoalList)) :
    currSubgoal = tmpSubgoalList[i]

    # provide extra closing parenthesis if previously removed
    if "(" in currSubgoal :
      if not ")" in currSubgoal :
        currSubgoal += ")"

    # remove starting comma, if present
    for j in range(0,len(currSubgoal)) :
      if (j == 0) and ( currSubgoal[j] == ",") :
        currSubgoal = currSubgoal[1:]

    # make sure empties do not sneak in
    if not "" == currSubgoal :
      subgoalList.append( currSubgoal )

  return subgoalList

####################
#  PARSE RELATION  #
####################
# input type of relationSpec ( fact || ruleHead || ruleBody ) and specifications of the relation
# input one fact, head EDB, or subgoal IDB only.
# output parsed relation specification [ relationName, [ attributes ], @arg, [additional args]  ]
#  if ruleHead, then additional args list will contain any aggregate functions
#  elif ruleBody, then additional args list will contain any subgoal keywords
def parseRelation( relationType, relationSpec ) :
  parsedRelationSpec = []

  # parse on '(' and ')'
  relationSpec = relationSpec.split( "(" ) # string becomes a list of strings
  specList = []
  for f in relationSpec :
    specList.extend( f.split( ")" ) )

  # restate meaning of each component for clarity
  relationName   = specList[0]
  attribList     = specList[1]
  atArg          = specList[2]
  additionalArgs = []

  # need to check for keywords
  if "ruleBody" == relationType :
    # notin keyword
    if "notin" in relationName : # note parseDedalus removed all whitespace
      relationName = relationName.replace( "notin", "" )
      additionalArgs.append( "notin" )

  # convert attribList from string to array
  attribList = attribList.replace( '"', '' ) # remove excess quotes
  attribList = attribList.split(",")

  # remove "@" symbol from atArg
  # assumes only one @ argument per relation
  atArg = atArg.replace( "@", "" )

  # populate newFact
  parsedRelationSpec.append( relationName )
  parsedRelationSpec.append( attribList )
  parsedRelationSpec.append( atArg )
  parsedRelationSpec.append( additionalArgs )

  #print parsedRelationSpec

  return parsedRelationSpec

################
#  PARSE FACT  #
################
# input fact
# output new fact to add to fact table
def parseFact( factLine ) :
  newFact = []

  # Observe the structure of a fact is practically identical 
  # to the structure of a rule body head or subgoal.
  newFact = parseRelation( "fact", factLine )

  #print "Fact : " + str(newFact)

  return newFact

################
#  PARSE RULE  #
################
# input rule
# output new rule to add to rule table
# schema [ headName, [ attributes ], @arg, [ additionalHeadOps ], 
#          [ subgoalName, [ attributes ], @arg, [ additionalBodyOps ] ] ]
def parseRule( ruleLine ) :
  newRule = []

  # split into head and body
  ruleLine = ruleLine.split( ":-" ) # string becomes array of strings

  # rename for clarity
  head = ruleLine[0]
  body = ruleLine[1]

  # parse the body into a list of subgoals
  subGoalList = getSubgoalList( body )

  # get parse of head
  parseHead = parseRelation( "ruleHead", head ) # [ relationName, [ attributes ], @arg, [additional args]  ]

  # get list of parsed subgoals
  parseBody = []
  for s in subGoalList :
    s = parseRelation( "ruleBody", s ) # [ relationName, [ attributes ], @arg, [additional args]  ]
    parseBody.append( s )

  # create the rule by combining the parsed head with the list of parsed subgoals
  newRule.append( parseHead )
  newRule.append( parseBody )

  #print "newRule = " + str(newRule)

  return newRule

################
#  CHECK RULE  #
################
# output true if line is a rule
def checkRule( line ) :
  if ":-" in line :
    return True
  else :
    return False

###################
#  PARSE DEDALUS  #
###################
# input raw dedalus file
# output contents in the tabular intermediate representations of rules and facts

# WARNING: CANNOT write rules or facts on multiple lines.
def parseDedalus( dedFile ) :
  factTable = Table( "FACT" ) # factTable( relationName, [ attributes ], @arg )
  ruleTable = Table( "RULE" ) # ruleTable( headName, [ attributes ], @arg, [ additionalHeadOps ],
                              #            [ subgoalName, [ attributes ], @arg, [ additionalBodyOps ] ] )

  # "always check if files exist" -- Olde SE proverb
  goodFileFlag = False
  if os.path.isfile( dedFile ) :
    goodFileFlag = True

  if goodFileFlag :
    f = open( dedFile, "r" )
    for line in f :
      # remove all whitespace        
      line = "".join( line.split() )

      # skip lines with comments and empy lines
      # => will not process lines with comments after the semicolon
      doNotSkip = True
      if "//" in line :
        doNotSkip = False
      elif "" == line :
        doNotSkip = False

      # process valid lines only
      if doNotSkip :
        if ";" in line :
          line = line.replace(";", "")   # remove semicolons
        else :
          sys.exit( "ERROR: Missing semicolon in line : \n" + line + "\nFYI: Cannot write Dedalus rules/facts on multiple lines. Aborting...")

        # sanity check number of parentheses
        sanityChecks.checkParentheses( line ) # exits here if number of '(' does not equal number of ')'

        if checkRule( line ) :
          newRule = parseRule( line ) # returns an array
          ruleTable.addRow( newRule ) # save new rule
        else :
          newFact = parseFact( line ) # returns an array
          factTable.addRow( newFact ) # save new fact

  else :
    sys.exit( "ERROR: File at " + dedFile + " does not exist.\nAborting..." )

  returnDict = {}
  returnDict[ "factTable" ] = factTable
  returnDict[ "ruleTable" ] = ruleTable

  print returnDict

  return returnDict # return as a dictionary instead of a tuple for backward compatibility

#########
#  EOF  #
#########
