#!/usr/bin/env python

import os, random, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import extractors, sanityChecks, parseCommandLineInput
import clockRelation
import dedalusParser
# ------------------------------------------------------ #

###################
#  GET RANDOM ID  #
###################
# input nothing
# output random 16 char alphanumeric id
def getID() :
  return "".join( random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16) )

###############
#  DED TO IR  #
###############
# input raw ded file
# store intermediate representation in SQL database
# output nothing
def dedToIR( filename, cursor ) :
  parsedLines = []
  parsedLines = dedalusParser.parseDedalus( filename ) # program exits here if file cannot be opened.

  for line in parsedLines :
    if line[0] == "fact" : # save facts
      name    = extractors.extractName(    line[1] )
      attList = extractors.extractAttList( line[1] )
      timeArg = extractors.extractTimeArg( line[1] )

      # generate random ID for fact
      fid = getID()

      # save fact name and time arg
      cursor.execute("INSERT INTO Fact VALUES ('" + fid + "','" + name + "','" + timeArg + "')")

      # save fact attributes
      attID = 0 # allows duplicate attributes in list
      for attName in attList :
        cursor.execute("INSERT INTO FactAtt VALUES ('" + fid + "','" + str(attID) + "','" + attName + "')")
        attID += 1

    elif line[0] == "rule" : # save rules
      goal        = extractors.extractGoal(    line[1] )
      goalName    = extractors.extractName(    goal    )
      goalAttList = extractors.extractAttList( goal    )
      goalTimeArg = extractors.extractTimeArg( goal    )

      subgoalList = extractors.extractSubgoalList( line[1] )

      print "goal        = " + str(goal)
      print "goalName    = " + str(goalName)
      print "goalAttList = " + str(goalAttList)
      print "goalTimeArg = " +  str(goalTimeArg)

      # generate random ID for goal
      rid = getID()

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

        # generate random ID for subgoal
        sid = getID()

        # save name, time arg, and additional args
        cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

        # save subgoal attributes
        attID = 0 # allows duplicate attributes in list
        for attName in goalAttList :
          cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "')")
          attID += 1

        # save subgoal additional args
        for addArg in subgoalAddArgs :
          cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

      # check for bugs
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

  return None

#################
#  IR TO CLOCK  #
#################
# input cursor and cmdline args, assume IR successful
# create the initial clock relation in SQL database
# output nothing
def IRToClock( cursor, argDict ) :
  clockRelation.initClockRelation( cursor, argDict )
  return None

######################
#  CLOCK TO DATALOG  #
######################
# input db cursor and path to save file
# read clock relation and generate datalog program
# save datalog program to a file
# output nothing
def clockToDatalog( cursor, datalogProgPath ) :
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
  # ded to IR
  dedToIR( dedFile, cursor )

  # IR to clock
  IRToClock( cursor, argDict )

  # clock to datalog (write to file)
  #clockToDatalog( cursor, datalogProgPath )

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
  cursor.execute('''CREATE TABLE IF NOT EXISTS FactAtt    (fid text, attID text, attName text)''')   # fact attributes list
  cursor.execute('''CREATE TABLE IF NOT EXISTS Rule       (rid text, goalName text, goalTimeArg text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS GoalAtt    (rid text, attID text, attName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Subgoals   (rid text, sid text, subgoalTimeArg text, subgoalAdditionalArgs text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS SubgoalAtt (rid text, sid text, attID text, attName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS SubgoalAddArgs (rid text, sid text, argName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Clock (src text, dest text, sndTime text)''')
  cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS IDX_Clock ON Clock(src, dest, sndTime)''') # make all clock row unique

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
