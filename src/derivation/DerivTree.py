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

DEBUG   = True
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
  def getTopology( self ) :
    nodes = []
    edges = []

    # add node
    if self.root.treeType == "goal" :
      nodes.append( (self.root.treeType, self.root.getName()+str(self.root.record)) )
    elif (self.root.treeType == "rule") or (self.root.treeType == "fact") :
      nodes.append( (self.root.treeType, self.root.getName()+str(self.root.bindings) ) )

    # add edge
    if not self.root.treeType == "fact" :
      for d in self.root.descendants :
        #edges.append( ( ( self.root.treeType, self.root.getName()), (d.root.treeType, d.root.getName()) ) )
        if self.root.treeType == "goal" :
          edges.append( ( (self.root.treeType, self.root.getName()+str(d.root.record)), (d.root.treeType, d.root.getName()+str(d.root.bindings)) ) )
        elif self.root.treeType == "rule" :
          edges.append( ( (self.root.treeType, self.root.getName()+str(d.root.bindings)), (d.root.treeType, d.root.getName()+str(d.root.bindings)) ) )

        topo = d.getTopology( )
        nodes.extend( topo[0] )
        edges.extend( topo[1] )

    return ( nodes, edges )

  # ------------------------------------------ #

  ##############
  #  GET ROOT  #
  ##############
  def getRoot( self ) :
    return self.root

  # ------------------------------------------ #
  #########################
  #  GENERATE DERIV TREE  #
  #########################
  # arg          := a list of subgoal dictionaries if creating new rules.
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
      goalInfo     = self.getGoalInfo( name, cursor )
      goalAtts     = goalInfo[0]
      goalRids     = goalInfo[1]
      fullInfo     = self.setBindings( name, record, goalAtts, cursor )
      provRuleName = fullInfo[0]
      fullBindings = fullInfo[1]
      allRules     = self.getGoalRules( goalRids, cursor )

      node     = GoalNode.GoalNode( name, isNeg, record )
      node.clearDescendants() # needed explicitly for some reason? >.>
      node.setDescendants( provRuleName, allRules, fullBindings, results, cursor )

    elif self.treeType == "fact" :
      if DEBUG_2 :
        print "HIT FACT : " + str(name) + ", " + str(record)
        #sys.exit("HIT FACT : " + str(name) + ", " + str(record))
      node     = FactNode.FactNode( name, isNeg, record, goalBindings )

    elif self.treeType == "rule" :
      if DEBUG_2 :
        print "HIT RULE : " + str(name) + ", " + str(record) + ", " + str(arg)
        #sys.exit("HIT RULE : " + str(name) + ", " + str(record))
      ruleInfo = self.getRuleInfo( name, cursor, arg )

      node     = RuleNode.RuleNode( name, ruleInfo, record, goalBindings )
      node.clearDescendants() # needed explicitly for some reason? >.>
      if DEBUG :
        print "node.getDescendants = " + str( node.getDescendants() )
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
  # rname = goal/rule name
  # arg   = [ { 'subgoalName' : ( isNeg bool, subgoalAtt [str] ) } ]
  # returns [ ( isNeg bool, subgoalName str, subgoalAtts [str] ) ]
  def getRuleInfo( self, rname, cursor, allRuleSubs ) :
    ruleInfo = []

    if DEBUG :
      print "... running getRuleInfo ..."

    #sys.exit( "BREAKPOINT: allSubs = " + str(allRuleSubs) )

    for ruleDict in allRuleSubs :
      for sub in ruleDict :
        name    = sub
        ruleTup = ruleDict[ sub ]
        isNeg   = ruleTup[0]
        attList = ruleTup[1]

        #sys.exit( "BREAKPOINT: name = " + str(name) + ", isNeg = " + str(isNeg) + ", attList = " + str(attList) )

        ruleInfo.append( (isNeg, name, attList) )

    #sys.exit( "BREAKPOINT: ruleInfo = " + str(ruleInfo) )
    return ruleInfo

  # ------------------------------------------ #
  ###################
  #  GET GOAL ATTS  #
  ###################
  def getGoalInfo( self, goalName, cursor ) :

    if DEBUG :
      print "... running getGoalInfo ..."

    # get all rids
    cursor.execute( "SELECT attID,attName,Rule.rid FROM Rule,GoalAtt WHERE Rule.goalName=='" + str(goalName) + "' AND Rule.rid==GoalAtt.rid" )
    namesrids = cursor.fetchall()
    namesrids = tools.toAscii_multiList( namesrids )

    attList = []
    ridList = []
    for r in namesrids :
      attList.append( r[1] )
      ridList.append( r[2] )

    # make sure ridList is a set
    ridList = set( ridList )

    # return the attribute list for the goal and
    # the list of rids for the goal
    return [ attList, ridList ]


  ##################
  #  SET BINDINGS  #
  ##################
  # record       = array of strings from evaluator results
  # goalAtts     = array of all attributes for the goal, including duplicates
  # goalBindings = array of tuples with existing maps from atts to values.
  def setBindings( self, name, record, goalAtts, cursor ) :
    if DEBUG :
      print "... running setBindings ..."
      print "record       = " + str(record)

    bindings = []  # list of tuples ( att, boundValue )

    # get prov rule name
    cursor.execute( "SELECT goalName FROM Rule" )
    nameList = cursor.fetchall()
    nameList = tools.toAscii_multiList( nameList )

    realProvName = []
    for n in nameList :
      if DEBUG :
        print "n = " + str(n)
      if (name in n[0]) and ("_prov" in n[0]) :
        realProvName.append( n[0] )

    # sanity check
    if len(realProvName) > 1 :
      sys.exit( "ERROR: more than one provenance rule for " +str(name) + " : " + str(realProvName) )
    elif len(realProvName) < 1 :
      sys.exit( "ERROR: no provenance rule for " +str(name) )
    else :
      realProvName = realProvName[0]

    # get all goal bindings
    cursor.execute( "SELECT attName,attID FROM Rule,GoalAtt WHERE Rule.goalName=='" + realProvName + "' AND Rule.rid==GoalAtt.rid" )
    provAtts = cursor.fetchall()
    provAtts = tools.toAscii_multiList( provAtts )

    if DEBUG :
      print "goalAtts = " + str( goalAtts )
      print "provAtts = " + str( provAtts )
      print "record   = " + str( record )

    # collect atts in order of appearance in the prov rule head
    attList = []
    for att in provAtts :
       attName = att[0]
       attList.append( attName )

    # assign atts to record values in left-to-right order.
    bindings = []
    for i in range(0,len(record)) :
      att  = attList[i]
      data = record[i]
      bindings.append( (att,data) )

    if DEBUG :
      print "bindings = " + str(bindings)

    return ( realProvName, bindings )


  ####################
  #  GET GOAL RULES  #
  ####################
  # returns a list of dictionaries connecting rule subgoals with associated atts
  # [ { 'subName0' : (isNegBool?, [subAtt0, ... , subattN]) }, 
  #     ..., 
  #   { 'subNameN' : (isNegBool?, [subAtt0, ... , subattN]) } ]
  def getGoalRules( self, ruleIDs, cursor ) :
    if DEBUG :
      print "... running getGoalRules ..."
      print "ruleIDs = " + str(ruleIDs)

    allSubs = []
    # populate allSubs
    for i in ruleIDs :
      currDict   = {}
      currSubIDs = []

      # get all sub names and all sub atts per name
      cursor.execute( "SELECT subgoalName,attID,attName FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + str(i) +  "' AND Subgoals.rid==SubgoalAtt.rid AND Subgoals.sid==SubgoalAtt.sid" )
      info = cursor.fetchall()
      info = tools.toAscii_multiList( info )

      print "info = " + str(info)

      for arr in info :
        name    = arr[0]
        attid   = arr[1]
        attName = arr[2]

        # get isNeg info
        cursor.execute( "SELECT argName FROM Subgoals,SubgoalAddArgs WHERE Subgoals.rid=='" + str(i) + "' AND Subgoals.subgoalName=='" + str(name) + "' AND Subgoals.rid==SubgoalAddArgs.rid"  )
        addInfo = cursor.fetchall()
        addInfo = tools.toAscii_multiList( addInfo )

        isNeg = addInfo[0][0]

        # populate currDict
        try :
          currDict[name][1].append( attName )
        except :
          currDict[name] = ( isNeg, [] )
          currDict[name][1].append( attName )

      subInfo = currDict
      allSubs.append( subInfo )

    if DEBUG :
      print "allSubs = " + str(allSubs)

    return allSubs


#########
#  EOF  #
#########
