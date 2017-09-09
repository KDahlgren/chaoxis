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
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." )  )

from utilities import tools

# **************************************** #

DEBUG = tools.getConfig( "SOLVERS", "ENCODEDPROVTREE_CNF_DEBUG", bool )

class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  rawformula = None  # a BooleanFormula, not neccessarily in CNF
  cnfformula = None  # a CNF formula string
  crashFacts = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ) :

    # -------------------------------------------------------------------------------- #
    # build raw formulas directly from rule-goal graphs
    self.rawformula            = self.convertToBoolean( provTree )
    self.rawformula_simplified = self.convertToBoolean_simplified( provTree )

    # -------------------------------------------------------------------------------- #
    # trees of AndFormulas and OrFormulas
    self.rawBooleanFmla_str            = self.rawformula.display()
    self.rawBooleanFmla_simplified_str = self.rawformula_simplified.display()

    # -------------------------------------------------------------------------------- #
    # convert the raw formulas into cnf
    # unsimplified version :
    self.cnfformula            = solverTools.convertToCNF( self.rawBooleanFmla_str )

    # simplified version :
    simp_raw_fmla              = self.simplify( self.rawBooleanFmla_simplified_str )
    simp_raw_fmla              = self.resolveParens( simp_raw_fmla )
    self.cnfformula_simplified = solverTools.convertToCNF( simp_raw_fmla )

    # clean crashFacts
    self.cleanCrashFacts()


  #######################
  #  CLEAN CRASH FACTS  #
  #######################
  # clean crash facts for formatting consistency
  def cleanCrashFacts( self ) :
    tmp = []
    for c in self.crashFacts :
      c = c.translate( None, string.whitespace )  # clean extra whitespace for consistency
      c = c.replace( "'", "" )                    # clean apostrophes for consistency
      tmp.append( c )
    self.crashFacts = tmp

  ##############
  #  SIMPLIFY  #
  ##############
  # simplify string versions of raw boolean formulas generated from prov trees
  # 1. removes all PLACEHOLDERS for non-clock facts
  # 2. removes all self comms
  # 3. removes all crashes and collects the crashes in the crashFact list attribute
  def simplify( self, fmla ) :

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

    # get list of all clock facts
    clockFactList = self.getClockFactList( fmla )

    # get subset representing crashes
    for cf in clockFactList :
      factTuple = self.getContents( cf )
      if factTuple[1] == "_" :
        self.crashFacts.append( cf )

    # remove crashes from fmla
    for cf in self.crashFacts :
      fmla = fmla.replace( cf, "_PLACEHOLDER_" )

    #tools.bp( __name__, inspect.stack()[0][3], "fmla = " + str( fmla ) )
    fmla = self.purgePlaceholders( fmla )

    return fmla


  #######################
  #  REMOVE SELF COMMS  #
  #######################
  def removeSelfComms( self, fmla ) :

    # get list of all clock facts
    clockFactList = self.getClockFactList( fmla )

    # get subset representing self comms
    selfComms = []
    for cf in clockFactList :
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

    factContents = clockFact[ openParen+2 : closedParen-1 ]
    factContents_list = factContents.split( ", " )

    temp = []
    for f in factContents_list :
      t = f.replace( "'", "" )
      temp.append( t )
    factContentsList = temp

    return factContentsList


  #########################
  #  GET CLOCK FACT LIST  #
  #########################
  def getClockFactList( self, fmla ) :

    clockFactList = [] # initialize

    # get starting indexes for clock substrings
    indexList = []
    for i in range( 0, len(fmla) ) :
      currChar = fmla[i]
      if i < len(fmla) - 8 :
        if fmla[i:i+8] == "clock(['" :
          indexList.append( i )
      else :
        break

    # retrive full clock facts
    for ind in indexList :
      clockFactList.append( fmla[ind:ind+27] )

    if not clockFactList == [] :
      return clockFactList
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


  ########################
  #  CONVERT TO BOOLEAN  #
  ########################
  def convertToBoolean( self, provTree ) :
  
    #if not provTree.isFinalState() :
    #  displayTree( provTree )
  
    fmla = None # initialize
  
    # -------------------------------------------------- #
    # case prov tree rooted at an ultimate goal
    #
    # always only one right goal => builds forumlas up from the left with parens:
    #    ( ( ... ) OP fmla_m-1 ) OP fmla_m
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
      if len( leftGoals ) > 1 :
        #fmla.left  = self.getLeftFmla( leftGoals, "OR" )
        fmla.left  = self.getLeftFmla( leftGoals, "AND" )
        fmla.right = self.convertToBoolean( rightGoal )
  
      elif len( leftGoals ) < 1 :
        fmla.unary = self.convertToBoolean( rightGoal )
  
      else : # leftGoals contains only one goal
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
    #    ( ( ... ) OP fmla_m-1 ) OP fmla_m
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
          fmla.left   = self.getLeftFmla_simplified( leftRules, "AND" )
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
          print " ...done adding _PLACEHOLDER to fmla."
  
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
  
    return fmla


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
