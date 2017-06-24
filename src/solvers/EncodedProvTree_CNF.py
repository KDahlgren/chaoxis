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
import inspect, os, sys

import AndFormula, OrFormula, Literal, solverTools

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #

DEBUG = tools.getConfig( "SOLVERS", "ENCODEDPROVTREE_CNF_DEBUG", bool )

class EncodedProvTree_CNF :

  ################
  #  ATTRIBUTES  #
  ################
  rawformula = None  # a BooleanFormula, not neccessarily in CNF
  cnfformula = None  # a CNF formula string


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, provTree ) :
    self.rawformula            = self.convertToBoolean( provTree )
    self.rawformula_simplified = self.convertToBoolean_simplified( provTree )
    self.rawBooleanFmla_str    = self.rawformula.display()
    self.cnfformula            = solverTools.convertToCNF( self.rawBooleanFmla_str )

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
          fmla.left   = self.getLeftFmla_simplified( leftRules, "AND" )
          fmla.right  = self.convertToBoolean_simplified( rightRule )
          fmla.unary  = None
  
        elif len( leftRules ) < 1 :
          fmla.left  = None
          fmla.unary = self.convertToBoolean_simplified( rightRule )
  
        else : # leftRules contains only one rule
          fmla.unary = None
          fmla.left  = self.convertToBoolean_simplified( leftRules[0] )
          fmla.right = self.convertToBoolean_simplified( rightRule )
  
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
