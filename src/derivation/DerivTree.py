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

DEBUG   = False
DEBUG_2 = True

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
  # results := complete dictionary of parsed results from the c4 dump
  # arg     := rule info in the case of a rule-based deriv tree, passed as None otherwise
  def __init__( self, n, t, i, record, results, cursor, arg, bindings ) :
    self.name     = n
    self.treeType = t
    self.isNeg    = i
    self.generateDerivTree( self.name, self.treeType, self.isNeg, record, results, cursor, arg, bindings )

  # ------------------------------------------ #

  ######################
  #  PRINT DERIV TREE  #
  ######################
  def printDerivTree( self ) :
    self.root.printTree()

  # ------------------------------------------ #

  ##################
  #  GET TOPOLOGY  #
  ##################
  def getTopology( self, nodes, edges ) :
    nodes.append( self.root.printNode() )

    if not self.root.treeType == "fact" :
      for d in self.root.descendants :
        if not d.treeType == "fact" :
          edges.append( ( self.root.printNode(), d.root.printNode() ) )

        topo = d.getTopology( [], [] )
        nodes.extend( topo[0] )
        edges.extend( topo[1] )

    return ( nodes, edges )

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
  # arg          := 
  # goalBindings := dictionary matching atts to values according to goal bindings; None if goal
  def generateDerivTree( self, name, treeType, isNeg, record, results, cursor, arg, goalBindings ) :
    if DEBUG :
      print "... running generateDerivTree ..."

    # -------------------------------- #
    # set root
    node = None
    if self.treeType == "goal" :
      if DEBUG_2 :
        print "HIT GOAL : " + str(name) + ", " + str(record)
        #sys.exit("HIT GOAL : " + str(name) + ", " + str(record))
      goalInfo = self.getGoalAtts( name, cursor )
      goalAtts = goalInfo[0]
      goalRids = goalInfo[1]
      bindings = self.setBindings( record, goalAtts, None )
      allRules = self.getGoalRules( goalRids, cursor )

      node     = GoalNode.GoalNode( name, isNeg, record )
      node.setDescendants( allRules, bindings, results, cursor )

    elif self.treeType == "fact" :
      if DEBUG_2 :
        print "HIT FACT : " + str(name) + ", " + str(record)
        #sys.exit("HIT FACT : " + str(name) + ", " + str(record))
      node     = FactNode.FactNode( name, isNeg, record )

    elif self.treeType == "rule" :
      if DEBUG_2 :
        print "HIT RULE : " + str(name) + ", " + str(record)
        #sys.exit("HIT RULE : " + str(name) + ", " + str(record))
      ruleInfo = self.getRuleInfo( name, cursor, arg )
      bindings = self.setBindings( record, ruleInfo, goalBindings )

      node     = RuleNode.RuleNode( ruleInfo, record, goalBindings )
      node.setDescendants( results, cursor )

    # -------------------------------- #
    # set the root of this derivation tree
    if node :
      self.root = node
    else :
      sys.exit( "DerivTree root assignment failed : \nroot = " + str( self.root ) + "\nname = " + str( self.name ) + "\ntreeType = " + str( self.treeType ) + "\nisNeg = " + str( self.isNeg ) + "\ndescendants = " + str( self.descendants )  )

  # ------------------------------------------ #
  # ------------------------------------------ #
  ###################
  #  GET RULE INFO  #
  ###################
  # returns [ ( isNeg bool, subgoalName str, subgoalAtts [str] ) ]
  def getRuleInfo( self, rname, cursor, arg ) :
    ruleInfo = []

    if DEBUG :
      print "... running getRuleInfo ..."

    ruleSubsDict = arg[2]

    for subgoal in ruleSubsDict :
      isNeg = False

      if DEBUG :
        print "subgoal = " + str(subgoal)

      info = ruleSubsDict[ subgoal ]
      extraArgsList = []
      for arg in info[0] :
        extraArgsList.extend( arg )

      if DEBUG :
        print "info          = " + str( info )
        print "extraArgsList = " + str( extraArgsList )

      # set sign of current subgoal
      if "notin" in extraArgsList :
        isNeg = True

      # set subgoal name
      subName = subgoal

      # get subgoal attribute list
      subgoalAtts = info[1]

      if DEBUG :
        print "isNeg       = " + str( isNeg )
        print "subName     = " + str( subName )
        print "subgoalAtts = " + str( subgoalAtts )

      ruleInfo.append( (isNeg, subName, subgoalAtts) )

    if DEBUG :
      print "ruleInfo = " + str( ruleInfo )

    return ruleInfo

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
  def setBindings( self, record, goalAtts, goalBindings ) :
    if DEBUG :
      print "... running setBindings ..."
      print "record       = " + str(record)
      print "goalAtts     = " + str(goalAtts)
      print "goalBindings = " + str(goalBindings)

    if goalBindings :
      bindings = []
      for att in goalAtts :
        for tup in goalBindings :
          if att == tup[0] :
            newTup = ( att, tup[1] )
            bindings.append( newTup )

    else :
      # -------------------------------------- #
      #            SANITY CHECKS               #
      if len( record ) > len( goalAtts ) :
        sys.exit( "*****************************\n*****************************\n>>> ERROR: number of data items in record exceeds number of attributes for the current goal : " + "\ngoalName = " + str(self.name) + "\nrecord = " + str(record) + "\ngoalAtts = " + str(goalAtts) )
      elif len( record ) < len( goalAtts ) :
        sys.exit( "*****************************\n*****************************\n>>> ERROR: number of data items in record less than number of attributes for the current goal : " + "\ngoalName = " + str(self.name) + "\nrecord = " + str(record) + "\ngoalAtts = " + str(goalAtts) )
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
