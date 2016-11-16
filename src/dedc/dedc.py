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
Equation       (rid text, eid text, eqn text)
Clock          (src text, dest text, sndTime text, delivTime text)

'''

import os, string, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import dumpers, extractors, tools, parseCommandLineInput
import clockRelation
import dedalusParser
import dedalusRewriter
import provenanceRewriter
import Fact, Rule
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDC_DEBUG = False
DEDC_DEBUG1 = True

###############
#  DED TO IR  #
###############
# input raw ded file
# store intermediate representation in SQL database
# output nothing
def dedToIR( filename, cursor ) :

  parsedLines = []
  parsedLines = dedalusParser.parseDedalus( filename ) # program exits here if file cannot be opened.

  # collect fact and rule metadata for future dumping
  factMeta = []
  ruleMeta = []

  # iterate over parsed lines
  for line in parsedLines :

    # ----------------------------------------------- #
    #                     FACTS                       #

    if line[0] == "fact" : # save facts

      # generate random ID for fact
      fid = tools.getID()

      # extract fact info
      name    = extractors.extractName(    line[1] )
      attList = extractors.extractAttList( line[1] )
      timeArg = extractors.extractTimeArg( line[1] )

      # save fact data in persistent DB using IR
      newFact = Fact.Fact( fid, cursor )
      newFact.setFactInfo( name, timeArg )
      newFact.setAttList(  attList       )

      # save fact metadata (aka object)
      factMeta.append( newFact )

      # check for bugs
      if DEDC_DEBUG :
        print "newFact.getName()    : " + str( newFact.getName()    )
        print "newFact.getAttList() : " + str( newFact.getAttList() )
        print "newFact.getTimeArg() : " + str( newFact.getTimeArg() )
        print "newFact.display() = " + newFact.display()

    # ----------------------------------------------- #
    #                     RULES                       #

    elif line[0] == "rule" : # save rules

      # generate a random ID for the rule
      rid = tools.getID()

      # --------------------------- #
      #            GOAL             #

      # extract goal info
      goal        = extractors.extractGoal(    line[1] )
      goalName    = extractors.extractName(    goal    )
      goalAttList = extractors.extractAttList( goal    )
      goalTimeArg = extractors.extractTimeArg( goal    )

      # check for bugs
      if DEDC_DEBUG :
        print "goal        = " + str(goal)
        print "goalName    = " + str(goalName)
        print "goalAttList = " + str(goalAttList)
        print "goalTimeArg = " +  str(goalTimeArg)

      # save rule goal info
      newRule = Rule.Rule(     rid, cursor           )
      newRule.setGoalInfo(     goalName, goalTimeArg )
      newRule.setGoalAttList(  goalAttList           )

      # check for bugs
      if DEDC_DEBUG :
        print "newRule.getGoalName()    : " + str( newRule.getGoalName()    )
        print "newRule.getGoalAttList() : " + str( newRule.getGoalAttList() )
        print "newRule.getGoalTimeArg() : " + str( newRule.getGoalTimeArg() )


      # --------------------------- #
      #           SUBGOALS          #

      # extract subgoal info
      subgoalList = extractors.extractSubgoalList( line[1] )

      # save subgoal name, time arg, and additional args
      for sub in subgoalList :

        # generate random ID for subgoal
        sid = tools.getID()

        subgoalName    = extractors.extractSubgoalName(    sub )
        subgoalAttList = extractors.extractAttList(        sub ) # returns list
        subgoalTimeArg = extractors.extractTimeArg(        sub )
        subgoalAddArgs = extractors.extractAdditionalArgs( sub ) # returns list

        # check for bugs
        if DEDC_DEBUG :
          print "subgoalName    = " + str(subgoalName)
          print "subgoalAttList = " + str(subgoalAttList)
          print "subgoalTimeArg = " + str(subgoalTimeArg)
          print "subgoalAddArgs = " + str(subgoalAddArgs)

        newRule.setSingleSubgoalInfo( sid, subgoalName, subgoalTimeArg )
        newRule.setSingleSubgoalAttList( sid, subgoalAttList )
        newRule.setSingleSubgoalAddArgs( sid, subgoalAddArgs )

      # check for bugs
      if DEDC_DEBUG :
        print "newRule.getSubgoalList = " + str( newRule.getSubgoalListStr() )

      # --------------------------- #
      #          EQUATIONS          #

      # extract equation info
      eqnList = extractors.extractEqnList( line[1] )

      for eqn in eqnList :
        # generate random ID for eqn
        eid = tools.getID()

        # save eqn
        newRule.setSingleEqn( eid, eqn )

      # check for bugs
      if DEDC_DEBUG :
        print "newRule.getEquationList() = " + newRule.getEquationListStr()

      # --------------------------- #

      ruleMeta.append( newRule )

      # check for bugs
      if DEDC_DEBUG :
        print "newRule.display() = " + newRule.display()

  # ----------------------------------------------------------- #

  return ( factMeta, ruleMeta )

#################
#  IR TO CLOCK  #
#################
# input cursor and cmdline args, assume IR successful
# create the initial clock relation in SQL database
# output nothing
def starterClock( cursor, argDict ) :
  clockRelation.initClockRelation( cursor, argDict )


########################
#  REWRITE TO DATALOG  #
########################
# input cursor, assume IR successful
# output nothing
def rewrite( ruleMeta, cursor ) :

  # rewrite intitial facts and rules
  dedalusRewriter.rewriteDedalus( cursor )

  # add provenance rules
  provenanceRewriter.rewriteProvenance( ruleMeta, cursor )


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
  meta     = dedToIR( dedFile, cursor )
  ruleMeta = meta[1]

  # generate the first clock
  starterClock( cursor, argDict )

  # dedalus and provenance rewrite to final IR
  rewrite( ruleMeta, cursor )

  # check for bugs
  if DEDC_DEBUG :
    dumpers.factDump( cursor )
    dumpers.ruleDump( cursor )
    dumpers.clockDump( cursor )

  # compile IR into C4 datalog
  #c4datalog()

  #return 

##############################
#  CREATE DEDALUS IR TABLES  #
##############################
def createDedalusIRTables( cursor ) :
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


def skip( line ) :
  line = line.translate( None, string.whitespace )
          
  if (not line == None) and (len(line) > 0) : # skip blank lines
    if (not line[0] == "/") and (not line[1] == "/") :
      return False

  return True

##################
#  GET INCLUDES  #
##################
# input a dictionary of file names and examinations statuses
# output a complete list of files associated with a particular Dedalus program

def getAllFiles( fileDict ) :

  # base case
  noMoreNewFiles = True
  for k,v in fileDict.items() :
    if v == False :
      noMoreNewFiles = False

  # unexplored files exist
  if not noMoreNewFiles :
    print "fileDict1 = " + str( fileDict )

    # iterate over all files
    for filename, status in fileDict.items() :

      # hit an unexplored file
      if status == False :

        # check if file exists
        filepath = os.path.abspath( filename )
        if os.path.isfile( filepath ) :
          infile = open( filename, 'r' )

          # iterate over all lines in input file
          for line in infile :
            if not skip( line ) :
              if "include" in line :
                line    = line.split( " " )
                newfile = line[1].translate( None, string.whitespace )
                fileDict[ newfile ] = False
          infile.close()
          fileDict[ filename ] = True

        else :
          sys.exit( "ERROR : file does not exist: " + str(filename) )

    print "fileDict2 = " + str( fileDict )
    fileDict = getAllFiles( fileDict )

  return fileDict

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
  createDedalusIRTables( cursor )

  # ----------------------------------------------------------------- #

  # get all input files
  dedfilename = ""
  fileDict    = {}
  for key in argDict :
    if "file" in key :
      dedfilename             = argDict[ key ]
      fileDict[ dedfilename ] = False

  fileDict = getAllFiles( fileDict )

  # compile all input dedalus files into a single datalog program
  for dedfilename, status in fileDict.items() :
    runCompiler( cursor, dedfilename, argDict, datalogProgPath )

  if DEDC_DEBUG1 :
    dumpers.factDump(  cursor )
    dumpers.ruleDump(  cursor )
    dumpers.clockDump( cursor )

  # ----------------------------------------------------------------- #

  IRDB.close()        # close db
  os.remove( saveDB ) # delete the IR file to clean up

  return datalogProgPath

#########
#  EOF  #
#########
