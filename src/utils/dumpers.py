#!/usr/bin/env python

'''
dumpers.py
   Methods for dumping specific contents from the database.
'''

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DUMPERS_DEBUG = False


###############
#  RULE DUMP  #
###############
# input database cursor
# output nothing, print all rules to stdout
def ruleDump( cursor ) :

  print "********************\nProgram Rules :"

  rules = []

  # --------------------------------------------------------------- #
  #                           GOALS                                 #

  # get all rule ids
  cursor.execute( "SELECT rid FROM Rule" )
  ruleIDs = cursor.fetchall()
  ruleIDs = tools.toAscii_list( ruleIDs )

  # iterate over rule ids
  newRule = []
  for i in ruleIDs :
    cursor.execute( "SELECT goalName FROM Rule WHERE rid == '" + i + "'" ) # get goal name
    goalName    = cursor.fetchone()
    goalName    = tools.toAscii_str( goalName )

    # get list of attribs in goal
    goalList    = cursor.execute( "SELECT attName FROM GoalAtt WHERE rid == '" + i + "'" )# list of goal atts
    goalList    = tools.toAscii_list( goalList )

    # get goal time arg
    goalTimeArg = ""
    cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid == '" + i + "'" )
    goalTimeArg = cursor.fetchone()
    goalTimeArg = tools.toAscii_str( goalTimeArg )

    # convert goal info to pretty string
    newRule.append( goalName + "(" )
    for j in range(0,len(goalList)) :
      if j < (len(goalList) - 1) :
        newRule.append( goalList[j] + "," )
      else :
        newRule.append( goalList[j] + ")" )
    if not goalTimeArg == "" :
      newRule.append( "@" + goalTimeArg + " :- " )
    else :
      newRule.append( " :- " )

    # --------------------------------------------------------------- #
    #                         SUBGOALS                                #

    # get list of sids for the subgoals of this rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid == '" + str(i) + "'" ) # get list of sids for this rule
    subIDs = cursor.fetchall()
    subIDs = tools.toAscii_list( subIDs )

    # iterate over subgoal ids
    for k in range(0,len(subIDs)) :
      s = subIDs[k]

      # get subgoal name
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + str(i) + "' AND sid == '" + str(s) + "'" )
      subgoalName = cursor.fetchone()

      if not subgoalName == None :
        subgoalName = tools.toAscii_str( subgoalName )

        if DUMPERS_DEBUG :
          print "subgoalName = " + subgoalName

        # get subgoal attribute list
        subAtts = cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + i + "' AND sid == '" + s + "'" )
        subAtts = tools.toAscii_list( subAtts )

        # get subgoal time arg
        cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + i + "' AND sid == '" + s + "'" ) # get list of sids for this rule
        subTimeArg = cursor.fetchone() # assume only one additional arg
        subTimeArg = tools.toAscii_str( subTimeArg )

        # get subgoal additional args
        cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + i + "' AND sid == '" + s + "'" ) # get list of sids for this rule
        subAddArg = cursor.fetchone() # assume only one additional arg
        if not subAddArg == None :
          subAddArg = tools.toAscii_str( subAddArg )
          subAddArg += " "
          newRule.append( subAddArg )

        # all subgoals have a name and open paren
        newRule.append( subgoalName + "(" )

        # add in all attributes
        for j in range(0,len(subAtts)) :
          if j < (len(subAtts) - 1) :
            newRule.append( subAtts[j] + "," )
          else :
            newRule.append( subAtts[j] + ")" )

        # conclude with time arg, if applicable
        if not subTimeArg == "" :
          newRule.append( "@" + subTimeArg )

        # cap with a comma, if applicable
        if k < len( subIDs ) - 1 :
          newRule.append( "," )

    # --------------------------------------------------------------- #
    #                         EQUATIONS                               #

    # get list of sids for the subgoals of this rule
    cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
    eqnIDs = cursor.fetchall()
    eqnIDs = tools.toAscii_list( eqnIDs )

    for e in range(0,len(eqnIDs)) :
      currEqnID = eqnIDs[e]
    
      # get associated equation
      if not currEqnID == None :
        cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + str(i) + "' AND eid == '" + str(currEqnID) + "'" )
        eqn = cursor.fetchone()
        if not eqn == None :
          eqn = tools.toAscii_str( eqn )

          # convert eqn info to pretty string
          newRule.append( "," + str(eqn) )

    # --------------------------------------------------------------- #

    newRule.append( " ;" ) # end all rules with a semicolon
    rules.append( newRule )
    newRule = []

  # print rules
  for r in rules :
    print ''.join(r)


###############
#  FACT DUMP  #
###############
# input database cursor
# output nothing, print all facts to stdout
def factDump( cursor ) :

  print "********************\nProgram Facts :"

  facts = []

  # get all fact ids
  cursor.execute( "SELECT fid FROM Fact" )
  factIDs = cursor.fetchall()
  factIDs = tools.toAscii_list( factIDs )

  # iterate over fact ids
  newFact = []
  for i in factIDs :
    cursor.execute( "SELECT name FROM Fact WHERE fid == '" + str(i) + "'" ) # get fact name
    factName    = cursor.fetchone()
    factName    = tools.toAscii_str( factName )

    # get list of attribs in fact
    factList    = cursor.execute( "SELECT attName FROM FactAtt WHERE fid == '" + str(i) + "'" ) # list of fact atts
    factList    = tools.toAscii_list( factList )

    # get fact time arg
    factTimeArg = ""
    cursor.execute( "SELECT timeArg FROM Fact WHERE fid == '" + i + "'" )
    factTimeArg = cursor.fetchone()
    factTimeArg = tools.toAscii_str( factTimeArg )

    # convert fact info to pretty string
    newFact.append( factName + "(" )
    for j in range(0,len(factList)) :
      if j < (len(factList) - 1) :
        newFact.append( factList[j] + "," )
      else :
        newFact.append( factList[j] + ")" )
    if not factTimeArg == "" :
      newFact.append( "@" + factTimeArg )

    newFact.append( " ;" ) # end all facts with a semicolon
    facts.append( newFact )
    newFact = []

  # print facts
  for f in facts :
    print ''.join(f)


################
#  CLOCK DUMP  #
################
# input db cursor
# output nothing, print all clock entries to stdout
def clockDump( cursor ) :
  print "********************\nProgram Clock :"
  clock = cursor.execute('''SELECT * FROM Clock''')
  for c in clock :
    print c

######################
#  RECONSTRUCT RULE  #
######################
# input a rule id, db cursor
# output full rule string
def reconstructRule( rid, cursor ) :
  return "TODO: output full rule string"

#########
#  EOF  #
######### 
