#!/usr/bin/env python

'''
EncodedProvTree.py
  code for encoding a given provenance tree
  borrows heavily from https://github.com/palvaro/ldfi-py
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, string, sys

import AndFormula, OrFormula, Literal, solverTools

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# ------------------------------------------------------ #
# import orik packages HERE!!!
if not os.path.abspath( __file__ + "/../../../lib/orik/src") in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/orik/src") )

from derivation import ProvTree

# **************************************** #

DEBUG = tools.getConfig( "SOLVERS", "ENCODEDPROVTREE_CNF_DEBUG", bool )

class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  simplified_cnf_fmla_list  = []
  crashFacts_list           = []
  status_list               = []   # list of booleans indicating whether fmla has clock facts.
                                   # False => no  clock facts in fmla
                                   # True  => yes clock facts in fmla

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ) :

    DISPLAY_RAW_FMLA = tools.getConfig( "SOLVERS", "DISPLAY_RAW_FMLA", bool )

    # -------------------------------------------------------------------------------- #
    # build raw formulas directly from rule-goal graphs

    # build simplified prov tree fmla (contains only the clock nodes relevant to execution provenance)
    provTreeList = self.getIndividualProvTreesFromFinalState( provTree )

    simplified_raw_fmla_list = []
    for provTree in provTreeList :
      simplified_raw_fmla_list.append( self.convertToBoolean_simplified( provTree ) )

    # -------------------------------------------------------------------------------- #
    # build string versions

    simplified_raw_fmla_list_str = []
    for fmla in simplified_raw_fmla_list :
      simplified_raw_fmla_list_str.append( fmla.display() )

    # -------------------------------------------------------------------------------- #
    # convert the raw formulas into cnf

    print "simplified_raw_fmla_list_str : " + str( simplified_raw_fmla_list_str )
    for fmla in simplified_raw_fmla_list_str :

      # CASE : formula contains no clock facts
      if not "clock([" in fmla :
        self.status_list.append( False )

      # CASE : formula contains clock facts
      else :

        # removes all PLACEHOLDERS for non-clock facts, all self comms
        new_fmla = self.simplify( fmla )

        # resolve parentheses, if applicable
        new_fmla = self.resolveParens( new_fmla )

        # generate final cnf version
        self.simplified_cnf_fmla_list.append( solverTools.convertToCNF( new_fmla ) )

        # clean crashFacts
        self.cleanCrashFacts()

        self.status_list.append( True )


  ################################################
  #  GET INDIVIDUAL PROV TREES FROM FINAL STATE  #
  ################################################
  def getIndividualProvTreesFromFinalState( self, fullProvTree ) :

    print "subtrees : " + str( fullProvTree.subtrees )

    # CASE : fullProvTree already references only a single post fact.
    if len( fullProvTree.subtrees ) > 0 and len( fullProvTree.subtrees ) < 1 :
      return [ fullProvTree ]

    # CASE : fullProvTree has multiple descendants
    elif len( fullProvTree.subtrees ) > 1 :

      treeList = []
      for i in range(0,len(fullProvTree.subtrees)) :
        print " i = " + str( i )
        newProvTree = self.getIndividualProvTreesFromFinalState_helper( i, fullProvTree )
        treeList.append( newProvTree )

      return treeList

    # CASE : no post facts?
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : whaaaaA? The final state has no descendants? How did we get this far? Aborting..." )


  #######################################################
  #  GET INDIVIDUAL PROV TREES FROM FINAL STATE HELPER  #
  #######################################################
  def getIndividualProvTreesFromFinalState_helper( self, index, fullProvTree ) :

    newProvTree = ProvTree.ProvTree( fullProvTree.rootname, fullProvTree.parsedResults, fullProvTree.cursor )
    newProvTree.subtrees = fullProvTree.subtrees
    newProvTree.nodeset  = fullProvTree.nodeset
    newProvTree.edgeset  = fullProvTree.edgeset
    newProvTree.subtrees = [ newProvTree.subtrees[index] ]

    return newProvTree


  #######################
  #  CLEAN CRASH FACTS  #
  #######################
  # clean crash facts for formatting consistency
  def cleanCrashFacts( self ) :

    tmp_list = []
    for crashList in self.crashFacts_list :
      tmp = []
      for c in crashList :
        c = c.translate( None, string.whitespace )  # clean extra whitespace for consistency
        c = c.replace( "'", "" )                    # clean apostrophes for consistency
        tmp.append( c )
      tmp_list.append( tmp )

    self.crashFact_list = tmp_list


  ##############
  #  SIMPLIFY  #
  ##############
  # simplify string versions of raw boolean formulas generated from prov trees
  # 1. removes all PLACEHOLDERS for non-clock facts
  # 2. removes all self comms
  # 3. removes all crashes and collects the crashes in the crashFact list attribute
  def simplify( self, fmla ) :

    print "in simplify : fmla = " + fmla

    simplified_fmla = self.purgePlaceholders( fmla )                   # remove PLACEHOLDERs
    simplified_fmla = self.removeSelfComms( simplified_fmla )          # remove self comms
    simplified_fmla = self.collectAndRemoveCrashes( simplified_fmla )  # remove crashes

    return simplified_fmla


  ####################
  #  RESOLVE PARENS  #
  ####################
  # fmla should contain only inter-node clock comms at this point with poorly resolved sets of parens. 
  def resolveParens( self, fmla ) :

    # get list of all clock facts
    clockFactList = self.getClockFactList( fmla )

    # resolve parens per clock fact according to patterns
    for cf in clockFactList :

      # PATTERN : (cf)
      if "(" + cf + ")" in fmla :
        fmla = fmla.replace( "(" + cf + ")", cf )
        return self.resolveParens( fmla )

      # PATTERN : ( cf)
      elif "( " + cf + ")" in fmla :
        fmla = fmla.replace( "( " + cf + ")", cf )
        return self.resolveParens( fmla )

      # PATTERN : (cf )
      elif "(" + cf + " )" in fmla :
        fmla = fmla.replace( "(" + cf + " )", cf )
        return self.resolveParens( fmla )

      # PATTERN : ( cf )
      elif "( " + cf + " )" in fmla :
        fmla = fmla.replace( "( " + cf + " )", cf )
        return self.resolveParens( fmla )

    # BASE CASE!!!
    return fmla


  ################################
  #  COLLECT AND REMOVE CRASHES  #
  ################################
  def collectAndRemoveCrashes( self, fmla ) :

    print "in collectAndRemoveCrashes : fmla = " + fmla

    # get list of all clock facts
    clockFactList = self.getClockFactList( fmla )

    print " in collectAndRemoveCrashes : clockFactList = " + str( clockFactList )

    # get subset representing crashes
    crashFacts = []
    for cf in clockFactList :

      print "Calling getContents from collectAndRemoveCrashes"

      factTuple = self.getContents( cf )
      if factTuple[1] == "_" :
        crashFacts.append( cf )

    # remove crashes from fmla
    for cf in crashFacts :
      fmla = fmla.replace( cf, "_PLACEHOLDER_" )

    #tools.bp( __name__, inspect.stack()[0][3], "fmla = " + str( fmla ) )
    fmla = self.purgePlaceholders( fmla )

    self.crashFacts_list.append( crashFacts )
    return fmla


  #######################
  #  REMOVE SELF COMMS  #
  #######################
  def removeSelfComms( self, fmla ) :

    print " in removeSelfComms : fmla = " + str( fmla )

    # get list of all clock facts
    clockFactList = self.getClockFactList( fmla )

    print " in removeSelfComms : clockFactList = " + str( clockFactList )

    # get subset representing self comms
    selfComms = []
    for cf in clockFactList :
      print "cf = " + str( cf )

      print "Calling getContents from removeSelfComms"

      factTuple = self.getContents( cf )
      if factTuple[0] == factTuple[1] :
        selfComms.append( cf )

    # remove self comms from fmla
    for sc in selfComms :
      fmla = fmla.replace( sc, "_PLACEHOLDER_" )

    fmla = self.purgePlaceholders( fmla )

    return fmla


  ##################
  #  GET CONTENTS  #
  ##################
  # input clock fact string
  # extract the data from the clock fact
  def getContents( self, clockFact ) :
  
    openParen   = None
    closedParen = None
    for i in range(0,len(clockFact)) :
      if clockFact[i] == "(" :
        openParen = i
      elif clockFact[i] == ")" :
        closedParen = i

    print "in getContents : clockFact = " + str( clockFact )

    factContents      = clockFact[ openParen+2 : closedParen-1 ]
    factContents_list = factContents.split( "," )

    print "in getContents : factContents      = " + str( factContents )
    print "in getContents : factContents_List = " + str( factContents_list )

    temp = []
    for f in factContents_list :
      t = f.replace( "'", "" )
      temp.append( t )
    factContentsList = temp

    return factContentsList


  #########################
  #  GET CLOCK FACT LIST  #
  #########################
  # get complete list of clock facts.
  # return after removing duplicates.
  def getClockFactList( self, fmla ) :

    # remove excess whitespace
    fmla = fmla.translate( None, string.whitespace)

    print "in getClockFactList : fmla = " + fmla

    clockList = [] # initialize

    # parse out all individual clock facts from fmla
    fmla = fmla.replace( "([", "__OPENPARENBRA__" )
    fmla = fmla.replace( "])", "__CLOSEBRAPAREN__" )
    fmla = fmla.replace( "(", "" )
    fmla = fmla.replace( ")", "" )

    fmla = fmla.split( "AND" )

    tmp = []
    for f in fmla :
      f = f.split( "OR" )
      tmp.extend( f )
    clockList = tmp

    # make unique
    tmp1 = []
    for s in clockList :
      if not s in tmp1 :
        tmp1.append( s )
    clockList = tmp1

    # restore original format
    tmp2 = []
    for c in clockList :
      c = c.replace( "__OPENPARENBRA__", "([" )
      c = c.replace( "__CLOSEBRAPAREN__", "])" )
      tmp2.append( c )
    clockList = tmp2

    if not clockList == [] :
      print "clockList = " + str( clockList )
      return clockList
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : no clock facts in fmla = " + str( fmla ) )


  ########################
  #  PURGE PLACEHOLDERS  #
  ########################
  # remove all placeholders from raw boolean formulas according to a set of recognized patterns.
  def purgePlaceholders( self, fmla ) :

    # CASE fmla already passed through simplification steps
    if "_PLACEHOLDER_" in fmla :

      # ----------------------------------------------------------------------------- #
      # AND
      if "( _PLACEHOLDER_ AND _PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( "( _PLACEHOLDER_ AND _PLACEHOLDER_ )", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      elif "( _PLACEHOLDER_ AND clock(" in fmla :
        splitfmla = fmla.split( "( _PLACEHOLDER_ AND clock(" )
        fmla      = "( clock(".join( splitfmla )
        return self.simplify( fmla )

      elif ") AND _PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( ") AND _PLACEHOLDER_ )", ") )" )
        return self.simplify( fmla )

      elif " ( _PLACEHOLDER_ ) AND " in fmla :
        fmla = fmla.replace( " ( _PLACEHOLDER_ ) AND ", "" )
        return self.simplify( fmla )

      elif " AND ( _PLACEHOLDER_ ) " in fmla :
        fmla = fmla.replace( " AND ( _PLACEHOLDER_ ) ", "" )
        return self.simplify( fmla )

      elif " _PLACEHOLDER_ AND " in fmla :
        fmla = fmla.replace( "_PLACEHOLDER_ AND ", "" )
        return self.simplify( fmla )

      # ----------------------------------------------------------------------------- #
      # OR
      elif "( _PLACEHOLDER_ OR _PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( "( _PLACEHOLDER_ OR _PLACEHOLDER_ )", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      elif "( _PLACEHOLDER_ OR clock(" in fmla :
        tools.bp( __name__, inspect.stack()[0][3], "TODO check this pattern: fmla = " + fmla )
        splitfmla = fmla.split( "( _PLACEHOLDER_ OR clock(" )
        fmla      = "( clock(".join( splitfmla )
        return self.simplify( fmla )

      elif ") OR _PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( ") OR _PLACEHOLDER_ )", ") )" )
        return self.simplify( fmla )

      elif " ( _PLACEHOLDER_ ) OR " in fmla :
        fmla = fmla.replace( " ( _PLACEHOLDER_ ) OR ", "" )
        return self.simplify( fmla )

      elif " OR ( _PLACEHOLDER_ ) " in fmla :
        fmla = fmla.replace( " OR ( _PLACEHOLDER_ ) ", "" )
        return self.simplify( fmla )

      # ----------------------------------------------------------------------------- #
      # UNARY
      elif "( _PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( "( _PLACEHOLDER_ )", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      elif "(_PLACEHOLDER_ )" in fmla :
        fmla = fmla.replace( "(_PLACEHOLDER_ )", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      elif "( _PLACEHOLDER_)" in fmla :
        fmla = fmla.replace( "( _PLACEHOLDER_)", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      elif "(_PLACEHOLDER_)" in fmla :
        fmla = fmla.replace( "(_PLACEHOLDER_)", "_PLACEHOLDER_" )
        return self.simplify( fmla )

      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized _PLACEHOLDER_ pattern in fmla = " + str(fmla) )

    # BASE CASE : no placeholders in fmla
    else :
      return fmla


  #############
  #  DISPLAY  #
  #############
  def display( self ) :
    return self.cnfformula


  #####################################
  #  CONVERT TO BOOLEAN (DEPRECATED)  #
  #####################################
  # input provTree object
  # output list of Boolean formula objects st one formula per post fact.
  def convertToBoolean( self, provTree ) :
  
    #if not provTree.isFinalState() :
    #  displayTree( provTree )
  
    fmla = None # initialize
  
    # -------------------------------------------------- #
    # case prov tree rooted at an ultimate goal
    #
    # always only one right goal => builds forumlas up from the left with parens:
    #    ( ( ( ... ) OP fmla_m-1 ) OP fmla_m )
    #
    # resulting formula 'AND's the prov trees of all post facts
    if provTree.isFinalState() :
      if len( provTree.subtrees ) > 0 :
        fmla      = AndFormula.AndFormula() # empty
        leftGoals = provTree.subtrees[:-1]  # of type list
        rightGoal = provTree.subtrees[-1]   # not a list
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: No results in post. Aborting execution..." )
  
      # branch on left rules contents
      if len( leftGoals ) > 1 :
        fmla.left  = self.getLeftFmla( leftGoals, "AND" )
        fmla.right = self.convertToBoolean( rightGoal )
  
      elif len( leftGoals ) < 1 :
        fmla.unary = self.convertToBoolean( rightGoal )
  
      else : # leftGoals contains only one goal
        fmla.left  = self.convertToBoolean( leftGoals[0] )
        fmla.right = self.convertToBoolean( rightGoal )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR1: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case prov tree rooted at goal
    elif provTree.root.treeType == "goal" :
  
      # case goal is negative => change when supporting negative provenance.
      if len( provTree.root.descendants ) == 0 :
        #fmla       = OrFormula.OrFormula()
        print " > Adding " + str( provTree.root ) + " to fmla unary."
        #fmla.unary = Literal.Literal( str( provTree.root ) )
        fmla       = Literal.Literal( str( provTree.root ) )
  
      # case goal has 1 or more rule descendants only
      elif self.checkDescendantTypes( provTree, "rule" ) :
        fmla      = OrFormula.OrFormula()          # empty
        leftRules = provTree.root.descendants[:-1] # of type list
        rightRule = provTree.root.descendants[-1]  # not a list
  
        # branch on left rules contents
        if len( leftRules ) > 1 :
          fmla.left   = self.getLeftFmla( leftRules, "AND" )
          fmla.right  = self.convertToBoolean( rightRule )
          fmla.unary  = None
  
        elif len( leftRules ) < 1 :
          fmla.left  = None
          fmla.unary = self.convertToBoolean( rightRule )
          #fmla.unary = "shit"
  
        else : # leftRules contains only one rule
          fmla.unary = None
          fmla.left  = self.convertToBoolean( leftRules[0] )
          fmla.right = self.convertToBoolean( rightRule )
  
      # case goal has one or more fact descendants only
      # goals with more than 1 fact contain wildcards
      #   Simplify representation by presenting the wilcard version
      #   because the wildcard fact is true if any of the underlying
      #   facts are true.
      elif self.checkDescendantTypes( provTree, "fact" ) :
        print " > Adding " + str( provTree.root ) + " to fmla."
        fmla = Literal.Literal( str( provTree.root ) ) # <--- BASE CASE!!!
        print " > Added " + str( provTree.root ) + " to fmla."
  
      # case universe implodes
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: goal unrecognized goal descendant pattern: provTree.root.descendants : " + str( provTree.root.descendants ) )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR2: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case prov tree rooted at rule
    elif provTree.root.treeType == "rule" :
      fmla      = AndFormula.AndFormula()        # empty
      leftGoals = provTree.root.descendants[:-1] # of type list
      rightGoal = provTree.root.descendants[-1]  # not a list
  
      # branch on left goals contents

      # CASE multiple left goals
      if len( leftGoals ) > 1 :
        #fmla.left  = self.getLeftFmla( leftGoals, "OR" )
        fmla.left  = self.getLeftFmla( leftGoals, "AND" )
        fmla.right = self.convertToBoolean( rightGoal )
  
      # CASE not left goals
      elif len( leftGoals ) < 1 :
        fmla.unary = self.convertToBoolean( rightGoal )
  
      # case only one left goal
      else :
        fmla.left  = self.convertToBoolean( leftGoals[0] )
        fmla.right = self.convertToBoolean( rightGoal )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR3: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case universe explodes
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: prov tree root is not an ultimate goal, a goal, or a rule: provTree.root.treeType = " + str( provTree.root.treeType ) )
  
    # sanity check
    if fmla.left and fmla.unary :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR4: self.left and self.unary populated for the same formula!")
  
    return fmla


  ###################################
  #  CONVERT TO BOOLEAN SIMPLIFIED  #
  ###################################
  def convertToBoolean_simplified( self, provTree ) :
  
    fmla = None # initialize
  
    # -------------------------------------------------- #
    # case prov tree rooted at an ultimate goal
    #
    # always only one right goal => builds forumlas up from the left with parens:
    #    ( ( ( ... ) OP fmla_m-1 ) OP fmla_m )
    #
    if provTree.isFinalState() :
      if len( provTree.subtrees ) > 0 :
        fmla      = AndFormula.AndFormula() # empty
        leftGoals = provTree.subtrees[:-1]  # of type list
        rightGoal = provTree.subtrees[-1]   # not a list
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: No results in post. Aborting execution..." )
  
      # branch on left rules contents
      if len( leftGoals ) > 1 :
        fmla.left  = self.getLeftFmla_simplified( leftGoals, "AND" )
        fmla.right = self.convertToBoolean_simplified( rightGoal )
  
      elif len( leftGoals ) < 1 :
        fmla.unary = self.convertToBoolean_simplified( rightGoal )
  
      else : # leftGoals contains only one goal
        fmla.left  = self.convertToBoolean_simplified( leftGoals[0] )
        fmla.right = self.convertToBoolean_simplified( rightGoal )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR1: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case prov tree rooted at goal
    elif provTree.root.treeType == "goal" :

      # case goal has no descendants
      if len( provTree.root.descendants ) == 0 :
        #print " > Adding " + str( provTree.root ) + " to fmla."
        #fmla = Literal.Literal( str( provTree.root ) )
        # only add clock facts to fmla, otherwise add placeholders
        print " > Adding _PLACEHOLDER_ to fmla."
        fmla = Literal.Literal( "_PLACEHOLDER_" )
  
      # case goal has 1 or more rule descendants only
      elif self.checkDescendantTypes( provTree, "rule" ) :
        fmla      = OrFormula.OrFormula()           # empty
        leftRules = provTree.root.descendants[:-1]  # of type list
        rightRule = provTree.root.descendants[-1]   # not a list
  
        # branch on left rules contents
        if len( leftRules ) > 1 :
          fmla.left   = self.getLeftFmla_simplified( leftRules, "OR" )
          #fmla.left   = self.getLeftFmla_simplified( leftRules, "AND" )
          fmla.right  = self.convertToBoolean_simplified( rightRule )
          fmla.unary  = None
  
        elif len( leftRules ) < 1 :
          fmla.left   = None
          fmla.unary  = self.convertToBoolean_simplified( rightRule )
  
        else : # leftRules contains only one rule
          fmla.unary  = None
          fmla.left   = self.convertToBoolean_simplified( leftRules[0] )
          fmla.right  = self.convertToBoolean_simplified( rightRule )
  
      # case goal has one or more fact descendants only
      # goals with more than 1 fact contain wildcards
      #   Simplify representation by presenting the wilcard version
      #   because the wildcard fact is true if any of the underlying
      #   facts are true.
      elif self.checkDescendantTypes( provTree, "fact" ) :
        # only add clock facts to formula, otherwise add placeholders
        if provTree.root.name == "clock" :
          print " > Adding " + str( provTree.root ) + " to fmla."
          fmla = Literal.Literal( str( provTree.root ) ) # <--- BASE CASE!!!
          print " ...done adding " + str( provTree.root ) + " to fmla."
        else :
          print " > Adding placeholder to fmla."
          fmla = Literal.Literal( "_PLACEHOLDER_" ) # <--- BASE CASE!!!
          print " ...done adding _PLACEHOLDER_ to fmla."
  
      # case universe implodes
      else :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: goal unrecognized goal descendant pattern: provTree.root.descendants : " + str( provTree.root.descendants ) )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR2: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case prov tree rooted at rule
    elif provTree.root.treeType == "rule" :
      fmla      = AndFormula.AndFormula()        # empty
      leftGoals = provTree.root.descendants[:-1] # of type list
      rightGoal = provTree.root.descendants[-1]  # not a list
  
      # branch on left goals contents
      if len( leftGoals ) > 1 :
        #fmla.left  = self.getLeftFmla_simplified( leftGoals, "OR" )
        fmla.left  = self.getLeftFmla_simplified( leftGoals, "AND" )
        fmla.right = self.convertToBoolean_simplified( rightGoal )
  
      elif len( leftGoals ) < 1 :
        fmla.unary = self.convertToBoolean_simplified( rightGoal )
  
      else : # leftGoals contains only one goal
        fmla.left  = self.convertToBoolean_simplified( leftGoals[0] )
        fmla.right = self.convertToBoolean_simplified( rightGoal )
  
      # sanity check
      if fmla.left and fmla.unary :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR3: self.left and self.unary populated for the same formula!")
  
    # -------------------------------------------------- #
    # case universe explodes
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: prov tree root is not an ultimate goal, a goal, or a rule: provTree.root.treeType = " + str( provTree.root.treeType ) )
  
    # sanity check
    if fmla.left and fmla.unary :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR4: self.left and self.unary populated for the same formula!")
 
    print "-------------------------------------------------------------"
    if fmla.left :
      print "fmla.left.display() = " + str( fmla.left.display() )
    else :
      print "fmla.left.display() = " + str( fmla.left )
    print 
    if fmla.left :
      print "fmla.right.display() = " + str( fmla.right.display() )
    else :
      print "fmla.right.display() = " + str( fmla.right )
    print
    if fmla :
      print "fmla = " + str( fmla.display() )
    else :
      print "fmla = " + str( fmla )
    print "-------------------------------------------------------------"

    #if self.rightSubfmlaContainsLeftSubfmla( fmla.left, fmla.right ) :
    #  tools.bp( __name__, inspect.stack()[0][3], "stophere"  )

    return fmla


  #########################################
  #  RIGHT SUBFMLA CONTAINS LEFT SUBFMLA  #
  #########################################
  def rightSubfmlaContainsLeftSubfmla( self, leftfmla, rightfmla ) :

    # -------------------------------------------- #
    # pass if either fmla is "None"
    if (not leftfmla) or (not rightfmla ) :
      return False

    # -------------------------------------------- #
    # find highest ops
    # split right fmla on highest ops
    # check if left fmla is a member of the right fmla component list.
    return True


  ##################
  #  FORMAT SYMPY  #
  ##################
  # replace all 'AND's with & and all 'OR's with | and all '_NOT_''s with ~
  def format_sympy( self, rawBooleanFmla ) :
  
    # return data
    sympy_expr        = None # type string
    sympy_symbol_list = None # type string
  
    cleanFmla = toggle_format_str( rawBooleanFmla, "valid_vars" )
  
    # --------------------------------------------------- #
    # populate sympy_expr
    tmp1       = "".join( cleanFmla.split() ) # remove all whitespace
    tmp2       = tmp1.replace( "AND" , " & " )
    tmp3       = tmp2.replace( "OR"  , " | " )
    tmp4       = tmp3.replace( "_NOT_" , " ~ " )
    sympy_expr = tmp4
  
    # --------------------------------------------------- #
    # populate sympy_symbol_list
    tmp1 = "".join( cleanFmla.split() )   # remove all whitespace
  
    tmp2 = tmp1.replace( "("  , ""           ) # remove all (
    tmp3 = tmp2.replace( ")"  , ""           ) # remove all )
    tmp4 = tmp3.replace( "~"  , ""           ) # remove all ~
    tmp5 = tmp4.replace( "AND", "__SOMEOP__" ) # replace ops with some common string
    tmp6 = tmp5.replace( "OR" , "__SOMEOP__" ) # replace ops with some common string
  
    tmp7 = tmp6.split( "__SOMEOP__" )          # get list of literal strings
    tmp8 = set( tmp7 )                         # remove all duplicates
  
    sympy_symbol_list = list( tmp8 )           # transform back into list to reduce headaches  
  
    # --------------------------------------------------- #
  
    return ( sympy_expr, sympy_symbol_list )
  
  
  ###########
  #  MERGE  #
  ###########
  def merge( self, subfmlas, op ) :
  
    fmla = None # initialize
  
    # branch on operator
    if op == "AND" :
      fmla = AndFormula.AndFormula() # empty
    elif op == "OR" :
      fmla = OrFormula.OrFormula()   # empty
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: unrecognized operator : " + str( op ) )
  
    # sanity check
    if fmla :
  
      # case multiple subformulas exist
      if len( subfmlas ) > 1 :
          fmla.left  = self.merge( subfmlas[:-1], op ) # subfmlas[:-1] is of type list
          fmla.right = self.merge( [ subfmlas[-1] ], op ) # subfmlas[-1] is of type BooleanFormula
  
      # case no subformulas exist
      elif len( subfmlas ) < 1 :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: subfmlas is empty." )
  
      # case only one subformula exists
      else :
        fmla.unary = subfmlas[0]
  
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: fmla does not exist." )
  
    return fmla
  
  
  ###################
  #  GET LEFT FMLA  #
  ###################
  def getLeftFmla( self, provTreeList, op ) :
  
    mergeFmla = None
    subfmlas = []
  
    for provTree in provTreeList :
      #displayTree( provTree )
      subfmlas.append( self.convertToBoolean( provTree ) )
  
    mergedFmla = self.merge( subfmlas, op )
  
    return mergedFmla
  

  ##############################
  #  GET LEFT FMLA SIMPLIFIED  #
  ##############################
  def getLeftFmla_simplified( self, provTreeList, op ) :

    mergeFmla = None
    subfmlas = []

    for provTree in provTreeList :
      #displayTree( provTree )
      subfmlas.append( self.convertToBoolean_simplified( provTree ) )

    mergedFmla = self.merge( subfmlas, op )

    return mergedFmla 

 
  ##################
  #  DISPLAY TREE  #
  ##################
  # input provenance tree
  # display relevant info about the tree to stdout
  # good for debugging
  def displayTree( self, tree ) :
    print
    print "----------------------------------------------------"
    print "  tree.root.name     = " + str( tree.root.name ) 
    print "  tree.root.treeType = " + str( tree.root.treeType )
    print "  tree.root.record   = " + str( tree.root.record )
    print "  tree.root.isNeg    = " + str( tree.root.isNeg ) 
    print "  len( tree.root.descendants ) = " + str( len( tree.root.descendants ) )
    for desc in tree.root.descendants :
      print "     desc.root.name               = " + str( desc.root.name ) 
      print "     desc.root.treeType           = " + str( desc.root.treeType )
      print "     desc.root.record             = " + str( desc.root.record )
      print "     desc.root.isNeg              = " + str( desc.root.isNeg ) 
      if not desc.root.treeType == "fact" :
        print "     len( desc.root.descendants ) = " + str( len( desc.root.descendants ) )
      else :
        print "     len( desc.root.descendants ) = 0"
  
  
  ############################
  #  CHECK DESCENDANT TYPES  #
  ############################
  def checkDescendantTypes( self, provTree, targetType ) :
  
    descList = provTree.root.descendants
  
    for d in descList :
      if not d.treeType == targetType :
        return False
  
    return True


#########
#  EOF  #
#########
