#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# ------------------------------------------------------ #
import provTree, GoalNode, RuleNode, FactNode

# ------------------------------------------------------ #

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #

DEBUG = True

# --------------------------------------------------- #
#                   DERIV TREE CLASS                  #
# --------------------------------------------------- #
class DerivTree( ) :

  #############
  #  ATTRIBS  #
  #############
  name        = None  # name of relation identifier
  treeType    = None  # goal, rule, or fact
  isNeg       = False # is goal negative? assume positive
  root        = None  # GoalNode, RuleNode, FactNode

  # ------------------------------------------ #
  #################
  #  CONSTRUCTOR  #
  #################
  # results == complete dictionary of parsed results from the c4 dump
  def __init__( self, n, t, i, record, results, cursor ) :
    self.name     = n
    self.treeType = t
    self.isNeg    = i
    self.generateDerivTree( self.name, self.treeType, self.isNeg, record, results, cursor )

  # ------------------------------------------ #
  ##############
  #  GET ROOT  #
  ##############
  def getRoot() :
    return root

  # ------------------------------------------ #
  #########################
  #  GENERATE DERIV TREE  #
  #########################
  def generateDerivTree( self, name, treeType, isNeg, record, results, cursor ) :
    if DEBUG :
      print "... running generateDerivTree ..."

    # -------------------------------- #
    # set root
    node = None
    if self.treeType == "goal" :
      goalInfo = self.getGoalAtts( name, cursor )
      goalAtts = goalInfo[0]
      goalRids = goalInfo[1]
      bindings = self.setBindings( record, goalAtts )
      allRules = self.getGoalRules( goalRids, cursor )

      node     = GoalNode.GoalNode( name, isNeg, record )
      node.setDescendants( allRules, bindings, results, cursor )

    elif self.treeType == "fact" :
      record      = getFactInfo( name )
      node        = FactNode.RuleNode( name, isNeg, record )
      node.setDescendants( results, cursor )

    elif self.treeType == "rule" :
      data         = getRuleInfo( name, cursor )
      origRuleDefs = data[0]
      bindings     = data[1]
      node         = RuleNode.RuleNode( name, isNeg, record )
      node.setDescendants( results, cursor )

    # -------------------------------- #
    # set the root of this derivation tree
    if node :
      root = node
    else :
      sys.exit( "DerivTree root assignment failed : \nroot = " + str( self.root ) + "\nname = " + str( self.name ) + "\ntreeType = " + str( self.treeType ) + "\nisNeg = " + str( self.isNeg ) + "\ndescendants = " + str( self.descendants )  )

  # ------------------------------------------ #
  ###################
  #  GET GOAL ATTS  #
  ###################
  # currently does a lot of extra work to generate the full dictionary, but only return the atts associated with the goalName.
  # return [ ]
  def getGoalAtts( self, goalName, cursor ) :

    if DEBUG :
      print "... running getGoalAtts ..."

    # get all rids
    cursor.execute( 'SELECT rid, goalName FROM Rule' )
    ridsNames = cursor.fetchall()
    ridsNames = tools.toAscii_multiList( ridsNames )

    # ------------------------------------------- #
    # get all rids with goal name as goalName
    targetDict = {}

    # prime dict
    for arr in ridsNames :
      goal = arr[1]
      targetDict[ goal ] = []

    # populate lists
    for arr in ridsNames :
      rid  = arr[0]
      goal = arr[1]

      targetDict[ goal ].append( rid )

    # ------------------------------------------- #
    # get goal atts

    cursor.execute( 'SELECT rid, attID, attName FROM GoalAtt' )
    goalAtts = cursor.fetchall()
    goalAtts = tools.toAscii_multiList( goalAtts )

    goalAttsDict = {}   # 'goal' : [ 'att0', ..., 'attN' ]

    # initialize goalAttsDict
    for g in targetDict :
      goalAttsDict[ g ] = []

    # populate goal att lists
    for g in targetDict :
      goal    = g
      ridList = targetDict[g]

      for r in ridList :
        for row in goalAtts :
          rid     = row[0]
          attID   = row[1]
          attName = row[2]

          if r == rid :
            goalAttsDict[ g ].append( attName )

    # ------------------------------------------- #
    if DEBUG :
      print "rids = " + str( ridsNames )
      print "targetDict = " + str( targetDict )
      print "goalAttsDict = " + str( goalAttsDict )

    # return the attribute list for the goal and
    # the list of rids for the goal
    return [ goalAttsDict[ goalName ], targetDict[ goalName ] ]


  ##################
  #  GET BINDINGS  #
  ##################
  def setBindings( self, record, goalAtts ) :
    if DEBUG :
      print "... running setBindings ..."
      print "record   = " + str(record)
      print "goalAtts = " + str(goalAtts)

    # -------------------------------------- #
    #            SANITY CHECKS               #
    if len( record ) > len( goalAtts ) :
      sys.exit( "ERROR: length of record exceeds number of attributes for the current goal : " + "\ngoalName = " + str(self.name) + "\nrecord = " + str(record) + "\ngoalAtts = " + str(goalAtts) )
    elif len( record ) < len( goalAtts ) :
      sys.exit( "ERROR: length of record less than number of attributes for the current goal : " + "\ngoalName = " + str(self.name) + "\nrecord = " + str(record) + "\ngoalAtts = " + str(goalAtts) )
    # -------------------------------------- #
    else :
      bindings = []  # list of tuples ( att, boundValue )
      for i in range(0,len(record)) :
        newTup = ( goalAtts[i], record[i] )
        bindings.append( newTup )

      if DEBUG :
        print "bindings = " + str(bindings)

      return bindings


  ####################
  #  GET GOAL RULES  #
  ####################
  # returns a list of rule id-rule detail tuples:
  #    [ (rid0, rule name, { 'att0' : (isNegBool?, [subAtt0, ... , subattN]), ..., 'attN' : (isNegBool?, [subAtt0, ... , subattN]) }), 
  #      ..., 
  #      (ridN, rule name, { 'att0' : (isNegBool?, [subAtt0, ... , subattN]), ..., 'attN' : (isNegBool?, [subAtt0, ... , subattN]) }) ]
  def getGoalRules( self, ruleIDs, cursor ) :
    if DEBUG :
      print "... running getGoalRules ..."
      print "ruleIDs = " + str(ruleIDs)

    cursor.execute( 'SELECT rid,sid,subgoalName FROM Subgoals' )
    subgoal = cursor.fetchall()
    subgoal = tools.toAscii_multiList( subgoal )

    allRules = []

    # populate allRules
    for i in ruleIDs :
      currDict   = {}
      currSubIDs = []

      # initialize this rule dictionary
      for row in subgoal :
        rid         = row[0]
        sid         = row[1]
        subgoalName = row[2]

        if i == rid :
          newData = [ None, [] ]

          # subgoal atts
          cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid == '" + str(i) + "' AND sid == '" + sid + "'" )
          info = cursor.fetchall()
          info = tools.toAscii_multiList( info )

          for att in info :
            newData[1].append( att[1] )

          # get subgoal neg bools
          cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + str(i) + "' AND sid == '" + sid + "'" )
          info2 = cursor.fetchall()
          info2 = tools.toAscii_multiList( info2 )
          newData[0] = info2

          currDict[ subgoalName ] = newData

          if DEBUG :
            print "currDict = " + str(currDict)
            print "info     = " + str( info )
            print "info2    = " + str( info2 )

      allRules.append( (i,self.name,currDict) )

    if DEBUG :
      print "allRules = " + str(allRules)

    return allRules


#########
#  EOF  #
#########
