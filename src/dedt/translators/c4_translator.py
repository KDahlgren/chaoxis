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
C4_TRANSLATOR_DEBUG   = False
C4_TRANSLATOR_DEBUG_1 = False


#####################
#  EXISTING DEFINE  #
#####################
# input subgoal name and list of currently accumulated define statements
# determine if a define already exists for the relation indicated by the subgoal
# output boolean

def existingDefine( name, definesNames ) :

  if name in definesNames :
    return True
  else :
    return False


################
#  C4 DATALOG  #
################
# input cursor for IR db
# output the full path for the intermediate file containing the c4 datalog program.

def c4datalog( table_list_path, datalog_prog_path, cursor ) :

  goalName         = None
  provGoalNameOrig = None

  tableListStr = "" # collect all table names delmited by a single comma only.

  # ----------------------------------------------------------- #
  # create goal defines

  # get all rids
  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  definesNames = []
  definesList  = []
  # ////////////////////////////////////////////////////////// #
  # populate defines list for rules
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
    if C4_TRANSLATOR_DEBUG :
      print "In c4datalog: definesList = " + str(definesList)

    if not existingDefine( goalName, definesNames ) : # prevent duplicates

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
      newDefine = ""
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
        definesNames.append( goalName )
        definesList.append( newDefine )
    # ////////////////////////////////////////////////////////// #

  # ----------------------------------------------------------- #
  # create fact defines

  # get all fact ids
  cursor.execute( "SELECT fid FROM Fact" )
  fidList = cursor.fetchall()
  fidList = tools.toAscii_list( fidList )

  for fid in fidList :

    # get goal name
    cursor.execute( "SELECT name FROM Fact WHERE fid = '" + fid + "'" )
    factName = cursor.fetchone()
    factName = tools.toAscii_str( factName )

    if C4_TRANSLATOR_DEBUG :
      print "**> factName = " + factName

    if C4_TRANSLATOR_DEBUG :
      print "In c4datalog: definesList = " + str(definesList)
    if not existingDefine( factName, definesNames ) : # prevent duplicates

      # populate table string
      tableListStr += factName + ","

      # get goal attribute list
      cursor.execute( "SELECT attID,attType From FactAtt WHERE fid = '" + fid + "'" )
      factAttList = cursor.fetchall()
      factAttList = tools.toAscii_multiList( factAttList )

      if C4_TRANSLATOR_DEBUG_1 :
        print "* factName = " + factName + ", factAttList " + str( factAttList )

      # populate type list for fact
      typeList = []
      for k in range(0,len(factAttList)) :
        att     = factAttList[ k ]
        attID   = att[0]
        attType = att[1]

        typeList.append( attType )

      # check for time argument
      cursor.execute( "SELECT timeArg FROM Fact WHERE fid='" + fid + "'" )
      timeArg = cursor.fetchone()
      timeArg = tools.toAscii_str( timeArg )

      if timeArg :
        typeList.append( "int" )

      # populate new c4 define statement
      newDefine = ""
      newDefine += "define("
      newDefine += factName
      newDefine += ",{"

      for i in range(0,len(typeList)) :
        newDefine += typeList[i]
        if i < len(typeList) - 1 :
          newDefine += ","
        else :
          newDefine += "});" + "\n"

      # save new c4 define statement
      if not newDefine in definesList :
        definesNames.append( factName )
        definesList.append( newDefine )
  # ////////////////////////////////////////////////////////// #

  # ----------------------------------------------------------- #
  # add clock define

  definesList.append( "define(clock,{string,string,int,int});\n" )
  tableListStr += "clock,"

  # ----------------------------------------------------------- #
  # add crash define

  definesList.append( "define(crash,{string,string,int});\n" )
  tableListStr += "crash"

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
  # add crash facts

  crashFactList = dumpers_c4.dump_crash( cursor )
  if C4_TRANSLATOR_DEBUG :
    print "c4_translator: crashFactList = " + str( crashFactList )

  # ----------------------------------------------------------- #
  # add rules

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  ruleList = []
  for rid in ridList :
    # verify data type compatibility for rules with equations
    verificationResults = tools.checkDataTypes( rid, cursor ) # returns array

    yesCompatible = verificationResults[0]
    offensiveEqn  = verificationResults[1]
    lhsType       = verificationResults[2]
    rhsType       = verificationResults[3]

    if yesCompatible :
      newRule = dumpers_c4.dumpSingleRule_c4( rid, cursor )
      ruleList.append( newRule )

    else : # data types are incompatible
      # throw error and abort
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: DATA TYPE INCOMPATABILITY\nAttempting to evaluate an equation in which variables possess incomparable types.\nERROR in line: " + dumpers_c4.dumpSingleRule_c4( rid, cursor )+ "\nERROR in eqn: " + offensiveEqn + "\nlhs is of type " + lhsType + " and rhs is of type " + rhsType )


  # ----------------------------------------------------------- #
  # save table list

  if C4_TRANSLATOR_DEBUG :
    print "*******************************************"
    print "table list str :"
    print tableListStr

  # save table list to file
  outfile = open( table_list_path, "w" )
  outfile.write( tableListStr )
  outfile.close()
  

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

  listOfStatementLists = [ definesList, factList, clockFactList, crashFactList, ruleList ]
  program              = tools.combineLines( listOfStatementLists )

  # save c4 program to file
  outfile = open( datalog_prog_path, "w" )
  outfile.write( program )
  outfile.close()


#########
#  EOF  #
#########
