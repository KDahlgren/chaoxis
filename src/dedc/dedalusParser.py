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

#from utils import tools, parseCommandLineInput
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
  name     = Word( alphanums + "_" )
  amp      = Literal( "@" )
  dquote   = Literal( '"' )
  squote   = Literal( "'" )
 
  prepend  = Literal( "notin" )

  numArg   = Word( nums )
  nextArg  = Literal( "next" )
  asyncArg = Literal( "async" )
  timeArg  = numArg | nextArg | asyncArg

  empty    = Word( "_" )
  baseAtt  = Word( alphanums ) | empty
  fatt1    = dquote + baseAtt + dquote #fact attribute version 1
  fatt2    = squote + baseAtt + squote #fact attribute version 2
  fatt     = fatt1 | fatt2
  ratt     = baseAtt                   # rule attribute
  semi     = Literal( ";" )

  fattList  = fatt + ZeroOrMore( Optional(",") + Optional( White() ) + fatt )
  rattList  = ratt + ZeroOrMore( Optional(",") + Optional( White() ) + ratt )
  
  comment  = Literal( "//" )
  commentLine  = ZeroOrMore( comment + alphanums + "_" )
  
  # define a fact
  fact = (name + paren + fattList + paren + semi + commentLine) | (name + paren + fattList + paren + amp + timeArg + semi + commentLine) | (prepend + name + paren + fattList + paren + semi + commentLine) | (prepend + name + paren + fattList + paren + amp + timeArg + semi + commentLine)
  
  # define a rule
  goal        = name + paren + rattList + paren + ZeroOrMore(amp + timeArg) 
  subgoal     = (goal + Optional( Optional( White() ) + semi + Optional(commentLine) )) | (prepend + goal + Optional( Optional( White() ) + semi ) + Optional(commentLine))
  subgoalList = subgoal + ZeroOrMore( Optional(",") + Optional( White() ) + subgoal )
  ruleOp      = Literal( ":-" )
  rule        = goal + ruleOp + subgoalList

  # return tuples
  if ";" in dedLine :
    if ":-" in dedLine :
      try :
        result = rule.parseString( dedLine )
        ret    = cleanResult( result )
        return ("rule", ret)
      except :
        sys.exit( "\nERROR: Invalid syntax in rule line : " + dedLine + "Note rule attributes cannot have quotes.\n")
    else :
      try :
        result = fact.parseString( dedLine )
        ret    = cleanResult( result )
        return ("fact", ret)
      except :
        sys.exit( "\nERROR: Invalid syntax in fact line : " + dedLine + "Note fact attributes must be surrounded by quotes.\n" )
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
