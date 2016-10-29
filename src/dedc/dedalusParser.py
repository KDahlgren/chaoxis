#!/usr/bin/env python

'''
dedalusParser.py
   Define the functionality for parsing Dedalus files.
'''

import os, sys
from pyparsing import alphanums, nums, Word, Literal, ZeroOrMore, Optional, White

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import sanityChecks, parseCommandLineInput
# ------------------------------------------------------ #

##################
#  CLEAN RESULT  #
##################
# input pyparse object of the form ([...], {...})
# output only [...]
def cleanResult( result ) :
  newResult = []

  numParsedStrings = len(result)
  for i in range(0, numParsedStrings) :
    newResult.append( result[i] )

  return newResult

###########
#  PARSE  #
###########
# input a ded line
# output parsed line
def parse( dedLine ) :
  # basic grammar
  paren    = Word( "()", exact=1 )
  name     = Word( alphanums )
  amp      = Literal( "@" )
  
  prepend  = Literal( "notin" )

  numArg   = Word( nums )
  nextArg  = Literal( "next" )
  asyncArg = Literal( "async" )
  timeArg  = numArg | nextArg | asyncArg
  
  baseAtt  = Word( alphanums )
  att1     = Optional('"') + baseAtt + Optional('"')
  att2     = Optional("'") + baseAtt + Optional("'")
  att      = att1 | att2
  semi     = Literal( ";" )
  attList  = att + ZeroOrMore( Optional(",") + Optional( White() ) + att )
  
  comment  = Literal( "//" )
  commentLine  = ZeroOrMore( comment + alphanums )
  
  # define a fact
  fact = (name + paren + attList + paren + semi + commentLine) | (name + paren + attList + paren + amp + timeArg + semi + commentLine) | (prepend + name + paren + attList + paren + semi + commentLine) | (prepend + name + paren + attList + paren + amp + timeArg + semi + commentLine)
  
  # define a rule
  goal        = name + paren + attList + paren + ZeroOrMore(amp + timeArg) 
  subgoal     = (goal + Optional( Optional( White() ) + semi + Optional(commentLine) )) | (prepend + goal + Optional( Optional( White() ) + semi ) + Optional(commentLine))
  subgoalList = subgoal + ZeroOrMore( Optional(",") + Optional( White() ) + subgoal )
  ruleOp      = Literal( ":-" )
  rule        = goal + ruleOp + subgoalList

  # return tuples
  if ";" in dedLine :
    if ":-" in dedLine :
      result = rule.parseString( dedLine )
      ret    = cleanResult( result )
      return ("rule", ret)
    else :
      result = fact.parseString( dedLine )
      ret    = cleanResult( result )
      return ("fact", ret)
  else :
    return None

###################
#  PARSE DEDALUS  #
###################
# input name of raw dedalus file
# output array of arrays containing the contents of parsed ded lines

# WARNING: CANNOT write rules or facts on multiple lines.
def parseDedalus( dedFile ) :
  parsedLines = []

  # "always check if files exist" -- Ye Olde SE proverb
  if os.path.isfile( dedFile ) :
    f = open( dedFile, "r" )
    for line in f :
      if "/" == line[0] : # skip lines beginning with a comment
        continue
      result = parse( line )
      if not result == None :
        parsedLines.append( result )

  else :
    sys.exit( "ERROR: File at " + dedFile + " does not exist.\nAborting..." )

  return parsedLines

#########
#  EOF  #
#########
