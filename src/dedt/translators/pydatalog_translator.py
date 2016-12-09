#!/usr/bin/env python

'''
pydatalog_translator.py
   Tools for producig pydatalog programs from the IR in the dedt compiler.
'''

import os, string, sqlite3, sys
import dumpers_pydatalog
import tools_pydatalog

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../.." )
sys.path.append( packagePath )

from utils import dumpers, extractors, tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
PYDATALOG_TRANSLATOR_DEBUG = False

operators = [ "+", "-", "*", "/", "<", ">", "<=", ">=" ]

#################
#  CREATE TERM  #
#################
# input a list of goal/subgoal names or literals
# output a pyDatalog create_term statement
def createTerm( strList ) :

  createTerm = ""
  createTerm += "pyDatalog.create_terms('"

  # remove all numbers as rule attributes
  tmp = []
  for s in strList :
    if not s.isdigit() :
      tmp.append( s )
  strList = tmp

  for i in range( 0, len(strList) ) :
    currItem = strList[i]
    for op in operators :
      if not op in currItem :
        createTerm += currItem
        break
      else :
        substr = ""
        for j in currItem :
          if not j == "+" :
            substr += j
          else :
            break
        createTerm += substr
        break
    if i < len(strList) - 1 :
      createTerm += ","
    else :
      createTerm += "')\n"

  return createTerm


########################
#  GET PYDATALOG PROG  #
########################
# input cursor for IR db
# output the full path for the intermediate file containing the pydatalog datalog program.

def getPyDatalogProg( cursor ) :

  list_names = []
  list_atts  = []
  list_wilds = []

  # ----------------------------------------------------------- #
  # get goal names and attributes

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  for rid in ridList :
    # get goal name
    cursor.execute( "SELECT goalName FROM Rule WHERE rid = '" + rid + "'" )
    goalName = cursor.fetchone()
    goalName = tools.toAscii_str( goalName )

    if not goalName in list_names :
      list_names.append( goalName )

    # get goal attribute list
    cursor.execute( "SELECT attName From GoalAtt WHERE rid = '" + rid + "'" )
    goalAttList = cursor.fetchall()
    goalAttList = tools.toAscii_list( goalAttList )

    for g in goalAttList :
      if not g in list_atts :
        list_atts.append( g )

  # ----------------------------------------------------------- #
  # create remaining subgoal create_terms statements

  for rid in ridList :
    # get list of all subgoal ids for the current rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + rid + "'" )
    subIDList = cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    for sid in subIDList :
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid = '" + rid + "' AND sid = '" + sid + "'" )
      subgoalName = cursor.fetchone()
      subgoalName = tools.toAscii_str( subgoalName )

      if not subgoalName in list_names :
        list_names.append( subgoalName )

      cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid = '" + rid + "' AND sid = '" + sid + "'" )
      subgoalAttList = cursor.fetchall()
      subgoalAttList = tools.toAscii_list( subgoalAttList )

      for s in subgoalAttList :
        if not s in list_atts :
          list_atts.append( s )

  # ----------------------------------------------------------- #
  #  populate new pydatalog create_terms statement

  if PYDATALOG_TRANSLATOR_DEBUG :
    print " >>> list_names :\n    " + str(list_names)
    print " >>> list_atts  :\n    " + str(list_atts)

  createTerm_names = createTerm( list_names )
  createTerm_atts = createTerm( list_atts )

  # ----------------------------------------------------------- #
  # add facts

  cursor.execute( "SELECT fid FROM Fact" )
  fidList = cursor.fetchall()
  fidList = tools.toAscii_list( fidList )

  factList = []
  for fid in fidList :
    newFact = dumpers_pydatalog.dumpSingleFact_pydatalog( fid, cursor )
    factList.append( newFact )

  # ----------------------------------------------------------- #
  # add clock facts

  clockFacts = dumpers_pydatalog.dumpClock_pydatalog( cursor )

  # ----------------------------------------------------------- #
  # add rules

  cursor.execute( "SELECT rid FROM Rule" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  ruleList = []
  for rid in ridList :
    newRule = dumpers_pydatalog.dumpSingleRule_pydatalog( rid, cursor )
    ruleList.append( newRule )

  # ----------------------------------------------------------- #
  # add wildcards

  # make a second pass over the rules to extract the complete set of
  #    random wildcards.
  for rule in ruleList :
    if PYDATALOG_TRANSLATOR_DEBUG :
      print ">>>> rule = " + str( rule )
    wildList = tools.attSearchPass2(rule)
    if PYDATALOG_TRANSLATOR_DEBUG :
      print " >>>>> attSearchPass2 = " + str( wildList )
    list_wilds.extend( wildList )

  createTerm_wilds = createTerm( list_wilds )

  # ----------------------------------------------------------- #
  # edit original rule list for goals with operators

  temp = []
  for rule in ruleList :
    cleanGoal   = tools_pydatalog.getGoal( rule )
    goalAttList = cleanGoal[2]

    flag = False
    for att in goalAttList :
      for op in operators :
        if op in att :
          flag = True

    # if a goal att contains an operator, then needs extra
    #   processing.
    if PYDATALOG_TRANSLATOR_DEBUG :
      print "HERE!"

    if flag :
      temp.extend( tools_pydatalog.opRules( rule ) )
    else :
      temp.append( rule )

  if len(temp) > 0 :
    ruleList = temp

  # ----------------------------------------------------------- #
  # save program

  if PYDATALOG_TRANSLATOR_DEBUG :
    print "*******************************************"
    print "createTerm_names :"
    print createTerm_names
    print "*******************************************"
    print "createTerm_atts :"
    print createTerm_atts
    print "*******************************************"
    print "createTerm_wilds :"
    print createTerm_wilds
    print "*******************************************"
    print "factList :"
    print factList
    print "*******************************************"
    print "clockFacts :"
    print clockFacts
    print "*******************************************"
    print "ruleList :"
    print ruleList

  listOfStatementLists = [ createTerm_names, createTerm_atts, createTerm_wilds, factList, clockFacts, ruleList ]
  program = tools.combineLines( listOfStatementLists )

  testpath = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/"
  programFilename = os.path.abspath( __file__ + "/../../.." ) + "/evaluators/programFiles/" + "pyDatalogProg.py"

  if os.path.isdir( testpath ) :
    outfile = open( programFilename, "w" )
    outfile.write( "import logging\n" )
    outfile.write( "from pyDatalog import pyDatalog, pyEngine\n" )
    outfile.write( "pyEngine.Logging = True\n" )
    outfile.write( "logging.basicConfig(level=logging.INFO)\n" )
    outfile.write( program )
    outfile.write( "print ( pre(X,Pl,SndTime) )\n" )
    outfile.write( "print ( post(X,Pl,SndTime) )\n" )
    outfile.close()
  else :
    sys.exit( "ERROR: directory for saving datalog program does not exist: " + testpath )

  return programFilename

#########
#  EOF  #
#########
