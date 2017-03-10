#!/usr/bin/env python

'''
extractors.py
  Define the functionality for extracting fact, goal, 
  and subgoal information from Dedalus facts and rules.
'''

import inspect, os, random, re, sqlite3, sys
from types import *

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
EXTRACTORS_DEBUG = False

specialOps = ["notin"] # TODO: make this configurable
eqnOps     = [ "+", "-", "*", "/", ">", "<", "<=", ">=", "==", "!=" ]

##################
#  IS LAST ITEM  #
##################
# input index and array length
# output boolean
def isLastItem( i, num ) :
  if i == num-1 :
    return True
  else :
    return False

############################
#  EXTRACT ADDITONAL ARGS  #
############################
# input parsed subgoal
# output list of additional args

def extractAdditionalArgs( parsedSubgoal ) :
  addList    = []

  if type( parsedSubgoal ) == list :
    for t in parsedSubgoal : # additional args are special ops
      for op in specialOps :
        if op in t :
          addList.append( op )

  elif type( parsedSubgoal ) == str :
    for op in specialOps :
      if op in parsedSubgoal :
        addList.append( op )

  return addList


##################
#  EXTRACT GOAL  #
##################
# input rule
# output goal array

def extractGoal( parsedLine ) :
  goal = []

  for c in parsedLine : # goal is anything appearing to the left of a ':-'
    if not c == ":-" :
      goal.append( c )
    else :
      break

  return goal


############
#  IS EQN  #
############
def isEqn( substr ) :
  for op in eqnOps :
    if op in substr :
      return True
  return False


######################
#  EXTRACT EQN LIST  #
######################
# input rule
# ouput list of eqn strings

def extractEqnList( parsedLine ) :

  groupedComponents = bodyParse( parsedLine )

  # only take eqns
  eqnList = [ comp for comp in groupedComponents if isEqn(comp) ]

  return eqnList


##########################
#  EXTRACT SUBGOAL LIST  #
##########################
# input rule
# ouput list of subgoal arrays

def extractSubgoalList( parsedLine ) :

  groupedComponents = bodyParse( parsedLine )

  # only take subgoals
  subgoalList = [ comp for comp in groupedComponents if ("(" in comp) and (")" in comp) ]

  return subgoalList


################
#  BODY PARSE  #
################
# group the contents of the rule body into subgoals and equantions/fmlas
# return list of groupings.
def bodyParse( parsedLine ) :

  # remove spaces for clarity
  newLine = []
  for i in range(0,len(parsedLine)) :
    if (not parsedLine[i] == " ") :
      newLine.append( parsedLine[i] )
  parsedLine = newLine

  # get rule body
  body = []
  flag = False
  for i in range(0,len(parsedLine)) :
    if parsedLine[i] == ":-" : # hit the rule operation
      flag = True              # signal start of body
      continue
    if flag :
      body = parsedLine[i:]    # save rest of list as body
      break

  # collect body components
  componentList = []
  oneComponent  = []

  # transform into string for ease of use 
  # (Pssstt...This means the parser is doing to much work >.> )
  # (TODO: tweak the parser or improve body processing)
  # (macabre language not intended.)
  body = "".join(body)

  # remove all @ args to prevent headaches
  body = re.sub( r'@[a-zA-Z0-9]', "", body )

  # split list on subgoal closed parens
  body = body.split( ")," )
  tmp = []
  for i in range(0,len(body)) :
    newComp = body[i]
    if i < len(body)-1 :
      newComp = newComp + ")"
    tmp.append( newComp )
  body = tmp

  # check for equations in body
  yesEqns = False
  for comp in body :
    for op in eqnOps :
      if op in comp :
        yesEqns = True

  # case rule has equations
  if yesEqns :
    for comp in body :
      if hasOp( comp ) :
        line = comp.split( "," )
        for i in range(0,len(line)) :
          item = line[i]
          if hasOp( item ) :
            componentList.append( item ) # save the equation
          else : # hit the start of a subgoal
            sub = ",".join( line[i:] )
            componentList.append( sub ) # save the subgoal
      else :
        componentList.append( comp )

  # case no equations
  else :
    componentList = body

  return componentList


############
#  HAS OP  #
############
def hasOp( substr ) :

  for op in eqnOps :
    if op in substr :
      return True

  return False

######################
#  EXTRACT TIME ARG  #
######################
# input fact or goal or subgoal
# output time arg

def extractTimeArg( parsedLine ) :
  timeArg = ""

  # case list, which will occur for facts
  if type( parsedLine ) == list :
    for i in range(0, len(parsedLine)) : # time arg immediately succeeds an ampersand
      if parsedLine[i] == "@" :
        try :
          timeArg = parsedLine[i+1]
        except :
          sys.exit( "ERROR: Missing time argument after '@' in " + str(parsedLine) )

  # case string, which will occur for rules
  elif type( parsedLine ) == str :
    aString = parsedLine
    for i in range(0,len(aString)) :
      aChar = aString[i]
      if aChar == "@" :
        try :
          timeArg = parsedLine[i+1]
        except :
          sys.exit( "ERROR: Missing time argument after '@' in " + str(parsedLine) )

  else :
    tools.bp( __name__, inspect.stack()[0][3], "parsedLine in not a list or a string: " + str(parsedLine) )

  return timeArg


######################
#  EXTRACT ATT LIST  #
######################
# input fact or goal or subgoal
# output attribute list

def extractAttList( parsedLine ) :
  attList   = []

  if type(parsedLine) is list : # occurs when parsed line is a fact
    saveFlag  = False
    skipChars = [ ",", "'", '"', " ", ";" ]
 
    for item in parsedLine : # save everything except the skip chars
      if item == '(' :
        saveFlag = True
        continue
      elif item == ')' :
        saveFlag = False
        continue
      elif item in skipChars :
        continue
      elif saveFlag :
        attList.append( item )

  elif type(parsedLine) is str : # occurs when parsedLine is a rule
    aString = parsedLine

    # .................................. #
    #if "@" in aString :
    #  print "aString = " + str(aString)
    #  tools.bp( __name__, inspect.stack()[0][3], "attList = " + str(attList) )
    # .................................. #

    for i in range(0,len(aString)) :
      aChar = aString[i]
      if aChar == "(" :

        for j in range(i, len(aString)) :
          if aString[j] == ")" :

            attList = aString[ i+1 : j ]
            attList = attList.split( "," )

            # .................................. #
            if "@" in aString :
              print "aString = " + str(aString)
              tools.bp( __name__, inspect.stack()[0][3], "attList = " + str(attList) )
            # .................................. #

            return attList


  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : parsedLine is not a list or a string:\n" + str(parsedLine) + "\ntype(parsedLine) = " + str(type(parsedLine)) )

  return attList


##########################
#  EXTRACT SUBGOAL NAME  #
##########################
# input parsed subgoal
# output name of subgoal

def extractSubgoalName( substr ) :

  for i in range(0,len(substr)) :
    if substr[i] == "(" :
      return substr[:i]

  return None # hit an equation


##################
#  EXTRACT NAME  #
##################
# input fact or goal
# output name of fact or goal

def extractName( parsedLine ) :
  return parsedLine[0] # assume name is the zeroth item in the parsed array


##########
#  MAIN  #
##########
if __name__ == "__main__" :
  extractEqnList(['timer_state', '(', 'H', 'I', 'T-1', ')', '@', 'next', ':-', 'timer_svc', '(', 'H', 'I', 'T', ')', ',', 'A', '(', 'B', 'C', ')', '@', '14'])
  extractEqnList(['timer_state', '(', 'H', 'I', 'T-1', ')', '@', 'next', ':-', 'timer_state', '(', 'H', 'I', 'T', ')', ',', '___notin___timer_cancel', '(', 'H', 'I', ')', ',', 'T>1'])
  extractEqnList(['timeout', '(', 'H', 'I', ')', ':-', 'timer_state', '(', 'H', 'I', '1', ')'])

#########
#  EOF  #
#########
