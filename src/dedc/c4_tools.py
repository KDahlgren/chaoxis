#!/usr/bin/env python

'''
c4_tools.py
   Tools for producig c4 datalog programs in dedc compiler.
'''

import os, string, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import dumpers, tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
C4_TOOLS_DEBUG = True


#####################
#  EXISTING DEFINE  #
#####################
# input subgoal name and list of currently accumulated define statements
# determine if a define already exists for the relation indicated by the subgoal
# output boolean

def existingDefine( name, definesList ) :
  for d in definesList :
    if name in d :
      return True
  return False

################
#  C4 DATALOG  #
################
# input cursor for IR db
# output the full path for the intermediate file containing the c4 datalog program.

def c4datalog( cursor ) :

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

    # prevent duplicates
    print "In c4datalog: definesList = " + str(definesList)
    if not existingDefine( goalName, definesList ) :
      # get goal attribute list
      cursor.execute( "SELECT attName From GoalAtt WHERE rid = '" + rid + "'" )
      goalAttList = cursor.fetchall()
      goalAttList = tools.toAscii_list( goalAttList )

      # populat type list for rule
      typeList = []
      for att in goalAttList :
        if "Time" in att :
          typeList.append( "int" )
        else :
          typeList.append( "string" )

      # populate new c4 define statement
      newDefine += "define("
      newDefine += goalName
      newDefine += ",{"

      for i in range(0,len(typeList)) :
        newDefine += typeList[i]
        if i < len(typeList) - 1 :
          newDefine += ","
        else :
          newDefine += "});"

      # save new c4 define statement
      definesList.append( newDefine )

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

      if not existingDefine( subgoalName, definesList ) :
        typeList       = []
        cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid = '" + rid + "' AND sid = '" + sid + "'" )
        subgoalAttList = cursor.fetchall()
        for att in subgoalAttList :
          if "Time" in att :
            typeList.append( "int" )
          else :
            typeList.append( "string" )

        newDefine += "define("
        newDefine += subgoalName + ",{"
        for i in range(0, len(typeList)) :
          if i < len(typeList) - 1 :
            newDefine += typeList[i] + ","
          else :
            newDefine += typeList[i] + "});"

        definesList.append( newDefine )

  # ----------------------------------------------------------- #
  # add facts

  cursor.execute( "SELECT fid FROM Fact" )
  fidList = cursor.fetchall()
  fidList = tools.toAscii_list( fidList )

  factList = []
  for fid in fidList :
    newFact = dumpers.dumpSingleFact( fid, cursor )
    factList.append( newFact )

  # ----------------------------------------------------------- #
  # add rules

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  ruleList = []
  for rid in ridList :
    newRule = dumpers.dumpSingleRule( rid, cursor )
    ruleList.append( newRule )

  # ----------------------------------------------------------- #
  # save program

  if C4_TOOLS_DEBUG :
    print "*******************************************"
    print "definesList :"
    print definesList
    print "*******************************************"
    print "factList :"
    print factList
    print "*******************************************"
    print "ruleList :"
    print ruleList

  program = tools.combineLines( definesList, factList, ruleList )

  testpath = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/"
  programFilename = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/" + "c4program.datalog"

  if os.path.isdir( testpath ) :
    outfile = open( programFilename, "w" )
    outfile.write( program )
    outfile.close()
  else :
    sys.exit( "ERROR: directory for saving datalog program does not exist: " + testpath )

  return programFilename


#########
#  EOF  #
#########
