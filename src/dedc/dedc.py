#!/usr/bin/env python

'''
dedc.py
   Define the functionality for converting parsed Dedalus into 
   SQL relations (the intermediate representation).
'''

'''
IR SCHEMA:

Fact           (fid text, name text, timeArg text)
FactAtt        (fid text, attID int, attName text)
Rule           (rid text, goalName text, goalTimeArg text)
GoalAtt        (rid text, attID int, attName text)
Subgoals       (rid text, sid text, subgoalName text, subgoalTimeArg text)
SubgoalAtt     (rid text, sid text, attID int, attName text)
SubgoalAddArgs (rid text, sid text, argName text)
Clock          (src text, dest text, sndTime text, delivTime text)

'''

import os, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import dumpers, extractors, tools, parseCommandLineInput
import clockRelation
import dedalusParser
import dedalusRewriter
import provenanceRewriter
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDC_DEBUG = True

###############
#  DED TO IR  #
###############
# input raw ded file
# store intermediate representation in SQL database
# output nothing
def dedToIR( filename, cursor ) :

  print " ... running dedToIR ..."

  parsedLines = []
  parsedLines = dedalusParser.parseDedalus( filename ) # program exits here if file cannot be opened.

  for line in parsedLines :

    print "in dedToIR: line = " + str(line)

    if line[0] == "fact" : # save facts
      name    = extractors.extractName(    line[1] )
      attList = extractors.extractAttList( line[1] )
      timeArg = extractors.extractTimeArg( line[1] )

      # generate random ID for fact
      fid = tools.getID()

      # save fact name and time arg
      cursor.execute("INSERT INTO Fact VALUES ('" + fid + "','" + name + "','" + timeArg + "')")

      # save fact attributes
      attID = 0 # allows duplicate attributes in list
      for attName in attList :
        cursor.execute("INSERT INTO FactAtt VALUES ('" + fid + "','" + str(attID) + "','" + attName + "')")
        attID += 1

    elif line[0] == "rule" : # save rules

      if DEDC_DEBUG :
        print "in dedc, processing rule " + str(line[1])

      # extract goal info
      goal        = extractors.extractGoal(    line[1] )
      goalName    = extractors.extractName(    goal    )
      goalAttList = extractors.extractAttList( goal    )
      goalTimeArg = extractors.extractTimeArg( goal    )

      # extract subgoal info
      subgoalList = extractors.extractSubgoalList( line[1] )

      # extract equation info
      eqnList     = extractors.extractEqnList( line[1] )

      # check for bugs
      if DEDC_DEBUG :
        print "goal        = " + str(goal)
        print "goalName    = " + str(goalName)
        print "goalAttList = " + str(goalAttList)
        print "goalTimeArg = " +  str(goalTimeArg)

      # generate random ID for goal
      rid = tools.getID()

      # save rule goal name and goal time arg
      cursor.execute("INSERT INTO Rule VALUES ('" + rid + "','" + goalName + "','" + goalTimeArg + "')")

      # save goal attributes
      attID = 0 # allows duplicate attributes in list
      for attName in goalAttList :
        cursor.execute("INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(attID) + "','" + attName + "')")
        attID += 1

      # save subgoal name, time arg, and additional args
      for sub in subgoalList :
        subgoalName    = extractors.extractSubgoalName(    sub )
        subgoalAttList = extractors.extractAttList(        sub ) # returns list
        subgoalTimeArg = extractors.extractTimeArg(        sub )
        subgoalAddArgs = extractors.extractAdditionalArgs( sub ) # returns list

        if DEDC_DEBUG :
          print "subgoalName    = " + str(subgoalName)
          print "subgoalAttList = " + str(subgoalAttList)
          print "subgoalTimeArg = " + str(subgoalTimeArg)
          print "subgoalAddArgs = " + str(subgoalAddArgs)

        # generate random ID for subgoal
        sid = tools.getID()

        # save name and time arg
        if not subgoalName == None :
          cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

        # save subgoal attributes
        attID = 0 # allows duplicate attributes in list
        for attName in subgoalAttList :
          cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "')")
          attID += 1

        # save subgoal additional args
        for addArg in subgoalAddArgs :
          cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

      # save eqns
      if DEDC_DEBUG :
        print "eqnList = " + str(eqnList)

      for eqn in eqnList :
        # generate random ID for eqn
        eid = tools.getID()

        # save eqn
        cursor.execute("INSERT INTO Equation VALUES ('" + rid + "','" + eid + "','" + eqn + "')")

      # check for bugs
      if DEDC_DEBUG :
        print "Rule :"
        Rule = cursor.execute('''SELECT * FROM Rule''')
        for r in Rule :
          print r
        print "GoalAtt :"
        GoalAtt = cursor.execute('''SELECT * FROM GoalAtt''')
        for g in GoalAtt :
          print g
        print "Subgoals :"
        Subgoals = cursor.execute('''SELECT * FROM Subgoals''')
        for s in Subgoals :
          print s
        print "SubgoalsAtt :"
        SubgoalAtt = cursor.execute('''SELECT * FROM SubgoalAtt''')
        for s in SubgoalAtt :
          print s
        print "SubgoalAdd :"
        SubgoalAdd = cursor.execute('''SELECT * FROM SubgoalAddArgs''')
        for s in SubgoalAdd :
          print s
        print "Equation :"
        eqns = cursor.execute('''SELECT * FROM Equation''')
        for s in eqns :
          print s

    if DEDC_DEBUG :
      dumpers.ruleDump( cursor )
      dumpers.factDump( cursor )

  return None

#################
#  IR TO CLOCK  #
#################
# input cursor and cmdline args, assume IR successful
# create the initial clock relation in SQL database
# output nothing
def StarterClock( cursor, argDict ) :
  clockRelation.initClockRelation( cursor, argDict )
  return None

########################
#  REWRITE TO DATALOG  #
########################
# input cursor, assume IR successful
# output nothing
def RewriteToDatalog( cursor ) :
  dedalusRewriter.rewriteDedalus( cursor )
  provenanceRewriter.rewriteProvenance( cursor )

  print "here!!!"

  # check for bugs
  if DEDC_DEBUG :
    dumpers.factDump( cursor )
    dumpers.ruleDump( cursor )

  return None

##################
#  RUN COMPILER  #
##################
# input db cursor, name of raw dedalus file, cmdline args, and path to datalog savefile
# convert ded files to IR
# use IR or cmdline args to create clock relation
# use IR and clock relation to create equivalent datalog program
# output nothing

# WARNING: CANNOT write rules or facts on multiple lines.
def runCompiler( cursor, dedFile, argDict, datalogProgPath ) :
  print " ... running compiler ..."

  # ded to IR
  dedToIR( dedFile, cursor )

  # generate the first clock
  #StarterClock( cursor, argDict )

  # dedalus and provenance rewrite to datalog
  #RewriteToDatalog( cursor )

  return None

#####################
#  COMPILE DEDALUS  #
#####################
# input command line arguments
# output abs path to datalog program
def compileDedalus( argDict ) :
  datalogProgPath = os.getcwd() + "/run.datalog"

  # instantiate IR database
  saveDB = os.getcwd() + "/IR.db"
  IRDB    = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor  = IRDB.cursor()

  # create tables
  cursor.execute('''CREATE TABLE IF NOT EXISTS Fact       (fid text, name text, timeArg text)''')    # fact names
  cursor.execute('''CREATE TABLE IF NOT EXISTS FactAtt    (fid text, attID int, attName text)''')   # fact attributes list
  cursor.execute('''CREATE TABLE IF NOT EXISTS Rule       (rid text, goalName text, goalTimeArg text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS GoalAtt    (rid text, attID int, attName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Subgoals   (rid text, sid text, subgoalName text, subgoalTimeArg text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS SubgoalAtt (rid text, sid text, attID int, attName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS SubgoalAddArgs (rid text, sid text, argName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Equation  (rid text, eid text, eqn text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Clock (src text, dest text, sndTime text, delivTime text)''')
  cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS IDX_Clock ON Clock(src, dest, sndTime, delivTime)''') # make all clock row unique

  # ----------------------------------------------------------------- #

  # compile all input dedalus files into a single datalog program
  for key in argDict :
    if "file" in key : # key to a ded file
      dedfilename = argDict[ key ]
      runCompiler( cursor, dedfilename, argDict, datalogProgPath )
    else : # this is not the ded file you're looking for. move along.
      continue # do nothing

  # ----------------------------------------------------------------- #

  # clear db  and clean up
  cursor.execute("DROP TABLE IF EXISTS Fact")
  cursor.execute("DROP TABLE IF EXISTS FactAtt")
  cursor.execute("DROP TABLE IF EXISTS Rule")
  cursor.execute("DROP TABLE IF EXISTS Subgoals")
  cursor.execute("DROP TABLE IF EXISTS SubgoalAtt")
  cursor.execute("DROP TABLE IF EXISTS GoalAtt")
  cursor.execute("DROP TABLE IF EXISTS Clock")
  cursor.execute("DROP INDEX IF EXISTS IDX_Clock")

  IRDB.close()        # close db
  os.remove( saveDB ) # delete the IR file to clean up

  return datalogProgPath

#########
#  EOF  #
#########
