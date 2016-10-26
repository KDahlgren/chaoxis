#!/usr/bin/env python

import os, random, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import sanityChecks, parseCommandLineInput
import dedalusParser
# ------------------------------------------------------ #

######################
#  EXTRACT TIME ARG  #
######################
# input fact or goal or subgoal
# output time arg
def extractTimeArg( parsedLine ) :
  timeArg = ""

  for i in range(0, len(parsedLine)) :
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
 
  for item in parsedLine : 
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

##################
#  EXTRACT NAME  #
##################
# input fact or goal or subgoal
# output name of fact or goal or subgoal
def extractName( parsedLine ) :
  return parsedLine[0]

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
      name    = extractName(    line[1] )
      attList = extractAttList( line[1] )
      timeArg = extractTimeArg( line[1] )

      # generate random ID
      fid = ''.join( random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16) )

      # save fact name and time arg
      cursor.execute("INSERT INTO Fact    VALUES ('" + fid + "','" + name + "','" + timeArg + "')")

      # save fact attributes
      attID = 0 # allows duplicate attributes in list
      for attName in attList :
        cursor.execute("INSERT INTO FactAtt VALUES ('" + fid + "','" + str(attID) + "','" + attName + "')")
        attID += 1

    elif line[0] == "rule" : # save rules
      print line[1]

  return None

#################
#  IR TO CLOCK  #
#################
# input nothing, assume IR successful
# create clock relation in SQL database
# output nothing
def IRToClock( cursor ) :
  return None

######################
#  CLOCK TO DATALOG  #
######################
# input nothing, assume IR successful
# read clock relation and generate datalog program
# save datalog program to a file
# output name of save file
def clockToDatalog( cursor ) :
  filename = ""
  return filename

##################
#  RUN COMPILER  #
##################
# input name of raw dedalus file
# output contents in the tabular intermediate representations of rules and facts

# WARNING: CANNOT write rules or facts on multiple lines.
def runCompiler( dedFile ) :
  saveDB = os.getcwd() + "/IR.db"
  IRDB    = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor  = IRDB.cursor()

  # create tables
  cursor.execute('''CREATE TABLE IF NOT EXISTS Fact       (fid text, name text, timeArg text)''')    # fact names
  cursor.execute('''CREATE TABLE IF NOT EXISTS FactAtt    (fid text, attID text, attName text)''')   # fact attributes list
  cursor.execute('''CREATE TABLE IF NOT EXISTS Rule       (rid text, goalName text, goalTimeArg text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS Subgoals   (rid text, sid text, subgoalTimeArg text, subgoalAdditionalArgs text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS SubgoalAtt (rid text, sid text, attName text)''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS GoalAtt    (rid text, attID text, attName text)''')

  # ded to IR
  dedToIR( dedFile, cursor )

  # TODO: dump fact tables contents to check for bugs.

  # IR to clock
  IRToClock( cursor )

  # clock to datalog (write to file)
  filename = clockToDatalog( cursor )

  # drop all tables to clean up
  cursor.execute("DROP TABLE IF EXISTS Fact")
  cursor.execute("DROP TABLE IF EXISTS FactAtt")
  cursor.execute("DROP TABLE IF EXISTS Rule")
  cursor.execute("DROP TABLE IF EXISTS Subgoals")
  cursor.execute("DROP TABLE IF EXISTS SubgoalAtt")
  cursor.execute("DROP TABLE IF EXISTS GoalAtt")

  IRDB.close()        # close db
  os.remove( saveDB ) # delete the IR file to clean up

  return filename

#########
#  EOF  #
#########
