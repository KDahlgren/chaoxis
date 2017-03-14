#!/usr/bin/env python

'''
c4.py
   Tools for producig c4 datalog programs from the IR in the dedt compiler.
'''

import inspect, os, re, string, sqlite3, sys
import dumpers_c4

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../.." )
sys.path.append( packagePath )

from utils import tools
from dedt  import Rule
# ------------------------------------------------------ #


#############
#  GLOBALS  #
#############
C4_TRANSLATOR_DEBUG   = True
C4_TRANSLATOR_DEBUG_1 = True


#####################
#  EXISTING DEFINE  #
#####################
# input subgoal name and list of currently accumulated define statements
# determine if a define already exists for the relation indicated by the subgoal
# output boolean

def existingDefine( name, definesList ) :

  for d in definesList :

    # preprocess string to get the table name only
    d = d.replace( "define(", "" ) # remove prepended define
    d = re.sub( r',{.*$\s', "", d )  # remove all the type info and the newline

    # check equality
    if name == d :
      return True

  return False


################
#  C4 DATALOG  #
################
# input cursor for IR db
# output the full path for the intermediate file containing the c4 datalog program.

def c4datalog( cursor ) :

  goalName         = None
  provGoalNameOrig = None

  tableListStr = "" # collect all table names delmited by a single comma only.

  # ----------------------------------------------------------- #
  # create goal defines

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  definesList = []
  for rid in ridList :
    newDefine   = ""

    # get goal name
    cursor.execute( "SELECT goalName FROM Rule WHERE rid = '" + rid + "'" )
    goalName = cursor.fetchone()
    goalName = tools.toAscii_str( goalName )

    # if it's a prov rule, get the original goal name
    provGoalNameOrig = None
    if "_prov" in goalName :
      provGoalNameOrig = goalName.split( "_prov" )
      provGoalNameOrig = provGoalNameOrig[0]

    # populate table string
    tableListStr += goalName + ","

    # ////////////////////////////////////////////////////////// #
    # populate defines list for rule goals
    print "In c4datalog: definesList = " + str(definesList)
    if not existingDefine( goalName, definesList ) : # prevent duplicates

      # get goal attribute list
      cursor.execute( "SELECT attID,attType From GoalAtt WHERE rid = '" + rid + "'" )
      goalAttList = cursor.fetchall()
      goalAttList = tools.toAscii_multiList( goalAttList )

      if C4_TRANSLATOR_DEBUG_1 :
        print "* goalName = " + goalName + ", goalAttList " + str( goalAttList )

      # populate type list for rule
      typeList = []
      for k in range(0,len(goalAttList)) :
        att     = goalAttList[ k ]
        attID   = att[0]
        attType = att[1]

        typeList.append( attType )

      # populate new c4 define statement
      newDefine += "define("
      newDefine += goalName
      newDefine += ",{"

      for i in range(0,len(typeList)) :
        newDefine += typeList[i]
        if i < len(typeList) - 1 :
          newDefine += ","
        else :
          newDefine += "});" + "\n"

      # save new c4 define statement
      if not newDefine in definesList :
        definesList.append( newDefine )
    # ////////////////////////////////////////////////////////// #

  # ----------------------------------------------------------- #
  # create remaining subgoal defines

  for rid in ridList :
    newDefine = ""

    # get list of all subgoal ids for the current rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + rid + "'" )
    subIDList = cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    for sid in subIDList :
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid = '" + rid + "' AND sid = '" + sid + "'" )
      subgoalName = cursor.fetchone()
      subgoalName = tools.toAscii_str( subgoalName )

      tableListStr += subgoalName + ","

      if not existingDefine( subgoalName, definesList ) :
        typeList       = []
        cursor.execute( "SELECT attID,attType FROM SubgoalAtt WHERE rid = '" + rid + "' AND sid = '" + sid + "'" )
        subgoalAttList = cursor.fetchall()
        subgoalAttList = tools.toAscii_multiList( subgoalAttList )

        # sanity check: all subgoal atts need a type
        for att in subgoalAttList :
          if "UNDEFINEDTYPE" in att[1] :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : subgoal '" + subgoalName + "' still has UNDEFINED attribute types:\nsubgoalAttList = " + str(subgoalAttList) )

        if C4_TRANSLATOR_DEBUG_1 :
          print "* subgoalName = " + subgoalName + ", subgoalAttList " + str( subgoalAttList )

        for att in subgoalAttList :
          attID   = att[0]
          attType = att[1]
          typeList.append( attType )

        # ................................................... #
        # handle clock define separately. Kind of hacky...
        if subgoalName == "clock" :
          cursor.execute( "SELECT * FROM SubgoalAtt WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
          res = cursor.fetchall()
          res = tools.toAscii_multiList( res )
          #tools.bp( __name__, inspect.stack()[0][3], "res = " + str(res) )
        #  continue
        # ................................................... #

        newDefine += "define("
        newDefine += subgoalName + ",{"
        for i in range(0, len(typeList)) :
          if i < len(typeList) - 1 :
            newDefine += typeList[i] + ","
          else :
            newDefine += typeList[i] + "}); //added in translator..." + "\n"

        if not newDefine in definesList :
          definesList.append( newDefine )

  # ----------------------------------------------------------- #
  # add facts

  cursor.execute( "SELECT fid FROM Fact" )
  fidList = cursor.fetchall()
  fidList = tools.toAscii_list( fidList )

  factList = []
  for fid in fidList :
    newFact = dumpers_c4.dumpSingleFact_c4( fid, cursor )
    factList.append( newFact )

  # ----------------------------------------------------------- #
  # add clock facts

  clockFactList = dumpers_c4.dump_clock( cursor )
  if C4_TRANSLATOR_DEBUG :
    print "c4_translator: clockFactList = " + str( clockFactList )

  # ----------------------------------------------------------- #
  # add rules

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  ruleList = []
  for rid in ridList :
    newRule = dumpers_c4.dumpSingleRule_c4( rid, cursor )
    ruleList.append( newRule )

  # ----------------------------------------------------------- #
  # save table list

  if C4_TRANSLATOR_DEBUG :
    print "*******************************************"
    print "table list str :"
    print tableListStr

  testpath_tables = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/"
  tablesFilename  = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/" + "tableListStr.data"

  if os.path.isdir( testpath_tables ) :
    outfile = open( tablesFilename, "w" )
    outfile.write( tableListStr )
    outfile.close()
  else :
    sys.exit( "ERROR: directory for saving tables for C4 Overlog program does not exist: " + testpath_tables )
  

  # ----------------------------------------------------------- #
  # save program

  if C4_TRANSLATOR_DEBUG :
    print "*******************************************"
    print "definesList :"
    print definesList
    print "*******************************************"
    print "factList :"
    print factList
    print "*******************************************"
    print "ruleList :"
    print ruleList

  listOfStatementLists = [ definesList, factList, clockFactList, ruleList ]
  program              = tools.combineLines( listOfStatementLists )

  testpath        = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/"
  programFilename = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/" + "c4program.olg"

  if os.path.isdir( testpath ) :
    outfile = open( programFilename, "w" )
    outfile.write( program )
    outfile.close()
  else :
    sys.exit( "ERROR: directory for saving C4 Overlog program does not exist: " + testpath )

  return [ tablesFilename, programFilename ]


#########
#  EOF  #
#########