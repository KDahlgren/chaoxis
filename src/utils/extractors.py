#!/usr/bin/env python

'''
extractors.py
  Define the functionality for extracting fact, goal, 
  and subgoal information from Dedalus facts and rules.
'''

import os, random, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

#from utils import tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
EXTRACTORS_DEBUG = True

specialOps = ["notin"] # TODO: make this configurable

########################
#  CHECK IF LAST ITEM  #
########################
# input index and array length
# output boolean
def checkIfLastItem( i, num ) :
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

  for t in parsedSubgoal : # additional args are special ops
    if t in specialOps :
      addList.append( t )

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


##################
#  CHECK IF EQN  #
##################
def checkIfEqn( substr ) :
  containsOpenParen = False
  containsClosedParen = False

  for c in substr :
    if c == "(" :
      containsOpenParen = True
    elif c == ")" :
      containsClosedParen = True

  # subgoal
  if containsOpenParen and containsClosedParen :
    return False
  else : # eqn
    return True

######################
#  EXTRACT EQN LIST  #
######################
# input rule
# ouput list of eqn strings

def extractEqnList( parsedLine ) :
  if EXTRACTORS_DEBUG :
    print "extractEqnList: parsedLine = " + str(parsedLine)

  eqnList = []
  opsList = ["+", "-", "*", "/", "<", ">", "<=", ">="]  #TODO: Make this configurable

  line = []

  # collect body only
  for i in range(0, len(parsedLine)) :
    if parsedLine[i] == ":-" :
      line = parsedLine[i+1:]

  # compile list of subgoals and eqns as strings
  subList = []
  currSub = ""
  for i in range(0, len(line)) :
    currChar = line[i]
    afterOpen = False

    if currChar == "(" :
      afterOpen = True
      currSub += currChar

    elif currChar == ")" :
      afterOpen = False
      currSub += currChar

    elif (currChar == ",") or (i == (len(line) - 1)) :
      if afterOpen and (currChar == ",") :
        currSub += currChar

      elif (i == (len(line) - 1)) :
        currSub += currChar
        subList.append( currSub )
        currSub = ""
        continue

      else :
        subList.append( currSub )
        currSub = ""
        continue

    else :
      currSub += currChar

  # gather equantions from list
  for substr in subList :
    if checkIfEqn( substr ) :
      eqnList.append( substr )

  # check for bugs
  if EXTRACTORS_DEBUG :
    print "subList = " + str(subList)
    print "eqnList = " + str(eqnList)

  return eqnList

##########################
#  EXTRACT SUBGOAL LIST  #
##########################
# input rule
# ouput list of subgoal arrays

def extractSubgoalList( parsedLine ) :
  subgoalList = []

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

  # iterate over body, subgoals delimited by commas
  oneSubgoal   = []
  inSubgoal    = False
  inTimeArg    = False
  endOfSubgoal = False
  for i in range(0,len(body)) :
    currItem = body[i]

    print "currItem   = " + str(currItem)
    print "oneSubgoal = " + str(oneSubgoal)

    if not checkIfEqn( currItem ) :
      print "here!"
      continue

    if currItem == "(" :
      inSubgoal = True
    elif currItem == ")" :
      inSubgoal = False
    elif currItem == "@" :
      inTimeArg = True
    elif (currItem == ",") and (not inSubgoal) :
      inTimeArg    = False
      endOfSubgoal = True

    if checkIfLastItem( i, len(body) ) :
      oneSubgoal.append( currItem )
      subgoalList.append( oneSubgoal )
      oneSubgoal = []
    if endOfSubgoal :
      subgoalList.append( oneSubgoal )
      oneSubgoal = []
      endOfSubgoal = False
      inSubgoal    = False
      inTimeArg    = False
    else :
      oneSubgoal.append( currItem )

  # double check for equations
  temp = []
  for c in subgoalList :
    if "(" in c :
      temp.append(c)
  subgoalList = temp

  if EXTRACTORS_DEBUG :
    print "extractors: subgoalList = " + str(subgoalList)

  return subgoalList


######################
#  EXTRACT TIME ARG  #
######################
# input fact or goal or subgoal
# output time arg

def extractTimeArg( parsedLine ) :
  timeArg = ""

  for i in range(0, len(parsedLine)) : # time arg immediately succeeds an ampersand
    if parsedLine[i] == "@" :
      try :
        timeArg = parsedLine[i+1]
      except :
        sys.exit( "ERROR: Missing time argument after '@' in " + str(parsedLine) )

  return timeArg


######################
#  EXTRACT ATT LIST  #
######################
# input fact or goal or subgoal
# output attribute list

def extractAttList( parsedLine ) :
  saveFlag  = False
  skipChars = [ ",", "'", '"', " ", ";" ]
  attList   = []
 
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

  return attList


##########################
#  EXTRACT SUBGOAL NAME  #
##########################
# input parsed subgoal
# output name of subgoal

def extractSubgoalName( parsedSubgoal ) :
  for t in parsedSubgoal :
    if not t in specialOps : # assume special operations only precede subgoal names
      return t


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
