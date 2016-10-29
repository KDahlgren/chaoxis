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

# from <name of sibling package> import <module name>, ...
# import <name of sibling package>
# ------------------------------------------------------ #

specialOps = ["notin"]

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
    if not parsedLine[i] == " " :
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
  flag         = False
  start        = 0
  beforeClose  = False
  for i in range(0,len(body)) :
    if body[i] == "(" :
      beforeClose = True # assumes all ")" are preceded by a matchin "("
    elif body[i] == ")" :
      beforeClose = False
    if ((body[i] == ",") or (body[i] == ";")) and (not beforeClose) :
      subgoalList.append( body[start:i] )  # save the subgoal
      start = i+1                          # don't save commas or semicolons

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


#########
#  EOF  #
#########
