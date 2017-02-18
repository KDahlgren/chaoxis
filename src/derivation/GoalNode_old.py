#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

import DerivTree

packagePath1  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath1 )
from Node import Node

packagePath2  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath2 )
from utils import tools

# **************************************** #

DEBUG = True

class GoalNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  isNeg       = False # is goal negative? assume positive
  descendants = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record, cursor ) :
    Node.__init__( self, "goal", name, record, None, cursor )
    self.isNeg    = isNeg

  ################
  #  PRINT TREE  #
  ################
  def printTree( self ) :
    print "********************************"
    print "           GOAL NODE"
    print "********************************"
    print "name   :" + str( self.name )
    print "isNeg  :" + str( self.isNeg )
    print "record :" + str( self.record )
    print "[ DESCENDANTS ]"
    for d in self.descendants :
      d.printDerivTree()

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    return "GOAL NODE: \nname = " + str( self.name ) + " ; \nisNeg = " + str( self.isNeg ) + ";\nbindings = " + str(self.bindings)


  ##################
  #  NODE DISPLAY  #
  ##################
  def nodeDisplay( self ) :
    return None

  #######################
  #  CLEAR DESCENDANTS  #
  #######################
  def clearDescendants( self ) :
    self.descendants = []

  #####################
  #  SET DESCENDANTS  #
  #####################
  # allRulesSubs := [ { ruleName : ( isNeg, [ (att,valbinding) ] ) } ]
  # fullBindings := [ ( ruleName, [ ( att, valbinding ) ] ) ]
  def setDescendants( self, provRuleName, allRulesSubs, fullBindings, results, cursor ) :
    #sys.exit( "BREAKPOINT: provRuleName = " + provRuleName )
    if DEBUG :
      print ">>> ... setting descendants ... <<<"
      print "   provRuleName = " + str( provRuleName )
      print "   allRulesSubs = " + str( allRulesSubs )
      print "   fullBindings = " + str( fullBindings )
      print "   results      = " + str( results )

    #if provRuleName == "log_prov" :
    #  sys.exit( "BREAKPOINT: allRulesSubs = " + str(allRulesSubs) )

    if len( fullBindings ) < 1 :
      sys.exit( "ERROR: no bindings for provenance rule " + provRuleName + ", given allRuleSubs = " + str( allRuleSubs ) )
    elif len( fullBindings ) > 1 :
      # collapse rule
      # if rule is recursively defined, then collapse the N rules used to describe the rule.
      # correct by substitution? (else revisit)
      origRuleName = provRuleName.split( "_" )
      origRuleName = origRuleName[0]

      res = self.collapseRule( origRuleName, allRulesSubs, fullBindings )
      fullBindings = res[0]
      allRulesSubs = res[1]

    # sanity check: make sure values of identical atts are identical per multi-rule goal
    for bind1 in fullBindings :
      for bind2 in fullBindings :
        att1 = bind1[0]
        val1 = bind1[1]
        att2 = bind2[0]
        val2 = bind2[1]
        if ( att1 == att2 ) and not ( val1 == val2 ) :
          origRuleName = provRuleName.split( "_" )
          origRuleName = origRuleName[0]
          sys.exit( "ERROR: multi-line rule possesses duplicate attribute names. Ensure attributes defined per rule are unique across rules for the same goal.\nOffending rule info:\noriginal rule name = " + str(origRuleName) + "\nprovRuleName = " + str(provRuleName) + "\nallRuleSubs = " + str(allRuleSubs) + "\nfullbindings = " + str(fullBindings) + "\nDuplicate bindings for " + att1 + " : \n" + str(bind1) + " and " + str(bind2)  )

    ######################
    tup           = fullBindings[0]
    self.schemaBindings = [] # needed for some reason??? graphs will not compile otherwise <.<
    self.setBindings( tup[1] )
    self.setOneDesc( provRuleName, allRulesSubs, results, cursor )

  ##################
  #  SET BINDINGS  #
  ##################
  def setBindings( self, allBindings ) :
    self.bindings = allBindings

    thisSchema = self.schema
    for attS in thisSchema :
      print "attS = " + attS
      for attTup in allBindings :
        if attS == attTup[0] :
          self.schemaBindings.append( attTup )

    self.schemaBindings = self.deduplicate_bindings( self.schemaBindings )
    #self.schemaBindings = list( set(self.schemaBindings) ) # ??? why needed ???

  ##########################
  #  DEDUPLICATE BINDINGS  #
  ##########################
  def deduplicate_bindings( self, schemaBinds ) :
    cleanList = []
    for bind in schemaBinds :
      if not bind in cleanList :
        cleanList.append( bind )
    return cleanList


  ##################
  #  SET ONE DESC  #
  ##################
  # allRulesSubs := [ { ruleName : ( isNeg, [ (att,valbinding) ] ) } ]
  def setOneDesc( self, provRuleName, allRulesSubs, results, cursor ) :

    #if provRuleName == "missing_log_prov" : 
    #  sys.exit( "BREAKPOINT : provRuleName = " + str(provRuleName) )

    #if provRuleName == "log_prov" : 
    #  sys.exit( "BREAKPOINT : provRuleName = " + str(provRuleName) + "\nallRulesSubs = " + str(allRulesSubs) )

    # sanity check
    if len( allRulesSubs ) > 1 :
      sys.exit( "ERROR: more than one dictionary of subgoals for rule " + provRuleName + "\nallRulesSubs = " + str(allRulesSubs) )
    elif len( allRulesSubs ) < 1 or ( {} in allRulesSubs ):
      sys.exit( "ERROR: zero subgoal dictionaries for rule " + provRuleName + "\nallRulesSubs = " + str(allRulesSubs) )

    else :
      for subDict in allRulesSubs :
        if DEBUG :
          print "provRuleName = " + str( provRuleName )
          print "GOALNODE : " + provRuleName + " processing rule expression from " + str(subDict)
        newRuleNode = DerivTree.DerivTree( provRuleName, "rule", False, self.record, results, cursor, allRulesSubs, self.bindings )
        self.descendants.append( newRuleNode )

      if DEBUG :
        print "provRuleName = " + str(provRuleName)
        print "GOALNODE : " + provRuleName + " has " + str(len(self.descendants)) + " descendants."
        print ">>> ... done setting descendants ... <<<"


  ###################
  #  COLLAPSE RULE  #
  ###################
  # fullBindings := [ ( ruleName, [ ( att, valbinding ) ] ) ]
  # return list of one tuple and updated allRulesSubs : 
  #   ( [ ( ruleName, [ ( att, valbinding ) ] ) ], [ { subRuleName : ( isNeg, [ (att,valbinding) ] ) } ] )
  def collapseRule( self, rname, allRulesSubs, fullBindings ) :
    #sys.exit( "BREAKPOINT: \nfullBindings = " + str( fullBindings ) + "\nallRulesSubs = " + str( allRulesSubs) )

    if DEBUG :
      print "allRulesSubs = " + str( allRulesSubs)

    #if rname == "log" :
    #  sys.exit( "BREAKPOINT1: rname = " + rname + ", allRulesSubs = " + str(allRulesSubs) )

    # create a single list of bindings
    bindingsComplete = []
    for tup in fullBindings :
      ruleName = tup[0]
      attArr   = tup[1]
      for attTup in attArr :
        bindingsComplete.append( attTup )

    # remove recursive subgoals from dicts
    newSubs = []
    if self.checkRuleRecursion( rname, allRulesSubs ) :
      for ruleSubs in allRulesSubs :
        #sys.exit( "BREAKPOINT ruleSubs = " + str(ruleSubs) )
        newDict = {}
        for sub in ruleSubs :
          if sub == rname :
            pass
          else :
            newDict[ sub ] = ruleSubs[ sub ]
        newSubs.append( newDict )

    # collapse new subs dicts into one dict
    newDict = {}
    print "newSubs = " + str(newSubs)
    for d in newSubs :
      print "d = " + str(d)
      for key in d :
        if type(key) is tuple :
          if key in newDict :
            newkey = key[0]+"-makeunique-"+tools.getID()
            while newkey in newDict :
              newkey = key[0]+"-"+tools.getID()
            newDict[newkey] = d[key] 
          else :
            newDict[key] = d[key]
        elif type(key) is str :
          if key in newDict :
            newkey = key+"-makeunique-"+tools.getID()
            while newkey in newDict :
              newkey = key+"-"+tools.getID()
            newDict[newkey] = d[key] 
          else :
            newDict[key] = d[key]

    #if rname == "log" :
    #  sys.exit( "BREAKPOINT: newDict = " + str(newDict) )

    return ( [ ( rname+"_prov", bindingsComplete ) ], [ newDict ] )


  ##########################
  #  CHECK RULE RECURSION  #
  ##########################
  # check if the current rule possesses any recursive definitions.
  def checkRuleRecursion( self, rname, allRulesSubs ) :
    for d in allRulesSubs :
      for key in d :
        if key[0] == rname :
          return True
    return False


#########
#  EOF  #
#########
