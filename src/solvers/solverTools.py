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
# python packages
import inspect, os, sys
from types import *
import sympy
from sympy.core import symbols
from sympy import *

import AndFormula, OrFormula, Literal
import Solver_PYCOSAT

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #


DEBUG = True


###############
#  SOLVE CNF  #
###############
def solveCNF( cnfFormula_str ) :

  print
  print "getConjuncts( cnfFormula_str ) = " + str( getConjuncts( cnfFormula_str ) )
  print

  # get solutions
  return Solver_PYCOSAT.Solver_PYCOSAT( cnfFormula_str )


###################
#  GET CONJUNCTS  #
###################
# return list of lists of disjunctive variables
def getConjuncts( cnfFormula_str ) :

  print
  print "cnfFormula_str = " + cnfFormula_str
  print

  # split on ANDs
  cnfFormula_str = cnfFormula_str.replace( "AND", "__AND__" )
  cnfFormula_str = cnfFormula_str.replace( "OR" , "__OR__"  )
  cnfFormula_str = "".join( cnfFormula_str.split() ) # remove whitespace
  cnfFormula_str = cnfFormula_str.replace( "__OR__" , " OR "  ) # to align with pycosat formatting
  clauses = cnfFormula_str.split( "__AND__" ) # divide clauses by the ANDs

  # clean strs
  cleanClauses = []
  for c in clauses :
    print "c = " + str( c )
    c = c.replace( "([", "__OPENPAR__" + "__OPENBRA__" )
    c = c.replace( "])", "__CLOSBRA__" + "__CLOSPAR__" )
    c = c.replace( ",", "__COMMA__" )
    c = c.replace( "(", "" )
    c = c.replace( ")", "" )
    cleanClauses.append( c )

  print "cleanClauses = " + str( cleanClauses )

  masterList = []
  # for clause in resulting list, collect a list of constituent vars
  # and add to master list.
  for c in cleanClauses :
    c = c.split( " OR " )
    masterList.append( c )

  print "masterList = " + str( masterList )

  return masterList


####################
#  CONVERT TO CNF  #
####################
# convert a raw boolean formula to cnf, if possible,
# using sympy.
def convertToCNF( rawBooleanFmla_str ) :

  cnfFmla = None

  # transform booleanFmla into the sympy format
  sympy_info = format_sympy( rawBooleanFmla_str ) # returns tuple of ( sympy formula string, symbol string )

  # run the transformed fmla through the smypy cnf converter
  res = toCNF_sympy( sympy_info )

  # transform the result back into the booleanFmla syntax
  cnfFmla = format_std( res )

  return cnfFmla


########################
#  TOGGLE FORMAT LIST  #
########################
def toggle_format_list( dirtyList, newFormat ) :

  cleanList = []

  for aStr in dirtyList :
    cleanList.append( toggle_format_str( aStr, newFormat ) )

  return cleanList

#######################
#  TOGGLE FORMAT STR  #
#######################
def toggle_format_str( dirtyStr, newFormat ) :

  if newFormat == "valid_vars" :
    # need to transform raw formula variables into legit Python variables.
    # also, remove all apostrophes/double quotes!
    # replace chars :
    #   [  --->  __OPENBRA__
    #   ]  --->  __CLOSBRA__
    #   (  --->  __OPENPAR__
    #   )  --->  __CLOSPAR__
    #   ,  --->  __COMMA__
    tmp0 = dirtyStr
    tmp0 = tmp0.replace( "'", "" )
    tmp0 = tmp0.replace( '"', "" )
    tmp1 = tmp0.replace( "[", "__OPENBRA__" )
    tmp2 = tmp1.replace( "]", "__CLOSBRA__" )
    tmp3 = tmp2.replace( "(", "__OPENPAR__" )
    tmp4 = tmp3.replace( ")", "__CLOSPAR__" )
    tmp5 = tmp4.replace( ",", "__COMMA__" )
    cleanResult = tmp5

  elif newFormat == "legible" :
    # transform back into legible syntax
    cleanResult = dirtyStr
    cleanResult = cleanResult.replace( "__OPENBRA__", "[" )
    cleanResult = cleanResult.replace( "__CLOSBRA__", "]" )
    cleanResult = cleanResult.replace( "__OPENPAR__", "(" )
    cleanResult = cleanResult.replace( "__CLOSPAR__", ")" )
    cleanResult = cleanResult.replace( "__COMMA__"  , "," )
    cleanResult = cleanResult

  else :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: unrecognized format requested: " + str( newFormat ) )

  return cleanResult


##################
#  FORMAT SYMPY  #
##################
# replace all 'AND's with & and all 'OR's with | and all 'NOT''s with ~
def format_sympy( rawBooleanFmla ) :

  # return data
  sympy_expr        = None # type string
  sympy_symbol_list = None # type string

  cleanFmla = toggle_format_str( rawBooleanFmla, "valid_vars" )

  # --------------------------------------------------- #
  # populate sympy_expr
  tmp1       = "".join( cleanFmla.split() ) # remove all whitespace
  tmp2       = tmp1.replace( "AND" , " & " )
  tmp3       = tmp2.replace( "OR"  , " | " )
  tmp4       = tmp3.replace( "NOT" , " ~ " )
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


##################
#  TO CNF SYMPY  #
##################
def toCNF_sympy( sympy_info ) :

  sympy_fmla          = sympy_info[0]
  sympy_symbol_string = sympy_info[1]

  # +++++++++++++++++++++++++++++++++++++++++++++++++++ #
  # to support large numbers of variables,
  # need to feed variables into sympy over the course
  # of multiple symbols() declaration statements.
  #
  # conservatively allot at most 3 fmla variables per 
  # declaration statement.
  #
  sympy_symbol_string_list3 = []
  newList                   = []
  for i in range( 0, len(sympy_symbol_string) ) :
    currsym = sympy_symbol_string[ i ]
    if i % 3 == 0 :
      newList.append( currsym )
      sympy_symbol_string_list3.append( newList )
      newList = []
    elif i + 1 == len( sympy_symbol_string ) :
      newList.append( currsym )
      sympy_symbol_string_list3.append( newList )
      newList = []
    else :
      newList.append( currsym )

  # build list of sympy symbol declaration strings
  symbol_str_list = []

  for varList in sympy_symbol_string_list3 :
    symbol_str = ""

    # left hand side
    for i in range( 0, len( sympy_symbol_string ) ) :
      var = sympy_symbol_string[ i ]
      if i < len( sympy_symbol_string ) - 1 : 
        symbol_str += var + ", "
      else :
        symbol_str += var

    # operator
    #symbol_str += ' = sympy.symbols("'
    symbol_str += ' = symbols("'

    # right hand side
    for i in range( 0, len( sympy_symbol_string ) ) :
      var = sympy_symbol_string[ i ]
      if i < len( sympy_symbol_string ) - 1 :
        symbol_str += var + ","
      else :
        symbol_str += var 

    # closing chars
    symbol_str += '")'

    symbol_str = symbol_str.replace("\'","")
    # add to list
    symbol_str_list.append( symbol_str )
  # +++++++++++++++++++++++++++++++++++++++++++++++++++ #
  
  # execute the symbol strings
  # (doing this step separately for clarity)
  for symbol_str in symbol_str_list :
    exec( symbol_str )

  # NOT the formula because LDFI is interested in the set of variable 
  #   assignments which render the original formula false.
  #   Therefore, need solutions for making !origfmla _true_.
  sympy_fmla = "~(" + sympy_fmla + ")"

  result = sympy.to_cnf( sympy_fmla, simplify=False )
  #result = sympy.to_cnf( sympy_fmla, simplify=True  ) # SLOW! even on simplelog (>.<)'

  # WARNING: sympy (rather sillily imo) overrides "replace" for Basic types.
  # bypassng with a format toggling function...
  result_str = toggle_format_str( str( result ), "legible" )

  #tools.bp( __name__, inspect.stack()[0][3], " result_str = "  + str(result_str) )

  return result_str


################
#  FORMAT STD  #
################
# non-trivial...
def format_std( sympy_fmla_res ) :

  fmla_std = None

  tmp0 = sympy_fmla_res
  tmp1 = tmp0.replace( "&", "AND" )
  tmp2 = tmp1.replace( "|", "OR" )
  tmp3 = tmp2.replace( "~", "NOT" )

  fmla_std = tmp3

  return fmla_std


########################
#  CONVERT TO BOOLEAN  #
########################
def convertToBoolean( provTree ) :

  if not provTree.isUltimateGoal() :
    displayTree( provTree )

  fmla = None # initialize

  # -------------------------------------------------- #
  # case prov tree rooted at an ultimate goal
  #
  # always only one right goal => builds forumlas up from the left with parens:
  #    ( ( ... ) OP fmla_m-1 ) OP fmla_m
  #
  if provTree.isUltimateGoal() :
    if len( provTree.subtrees ) > 0 :
      fmla      = AndFormula.AndFormula() # empty
      leftGoals = provTree.subtrees[:-1]  # of type list
      rightGoal = provTree.subtrees[-1]   # not a list
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: No results in post. Aborting execution..." )

    # branch on left rules contents
    if len( leftGoals ) > 1 :
      fmla.left = getLeftFmla( leftGoals, "AND" )
      fmla.right  = convertToBoolean( rightGoal )

    elif len( leftGoals ) < 1 :
      fmla.unary = convertToBoolean( rightGoal )

    else : # leftGoals contains only one goal
      fmla.left  = convertToBoolean( leftGoals[0] )
      fmla.right = convertToBoolean( rightGoal )

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
    elif checkDescendantTypes( provTree, "rule" ) :
      fmla      = OrFormula.OrFormula()          # empty
      leftRules = provTree.root.descendants[:-1] # of type list
      rightRule = provTree.root.descendants[-1]  # not a list

      # branch on left rules contents
      if len( leftRules ) > 1 :
        fmla.left   = getLeftFmla( leftRules, "AND" )
        fmla.right  = convertToBoolean( rightRule )
        fmla.unary  = None

      elif len( leftRules ) < 1 :
        fmla.left  = None
        fmla.unary = convertToBoolean( rightRule )
        #fmla.unary = "shit"

      else : # leftRules contains only one rule
        fmla.unary = None
        fmla.left  = convertToBoolean( leftRules[0] )
        fmla.right = convertToBoolean( rightRule )

    # case goal has one or more fact descendants only
    # goals with more than 1 fact contain wildcards
    #   Simplify representation by presenting the wilcard version
    #   because the wildcard fact is true if any of the underlying
    #   facts are true.
    elif checkDescendantTypes( provTree, "fact" ) :
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
      #fmla.left  = getLeftFmla( leftGoals, "OR" )
      fmla.left  = getLeftFmla( leftGoals, "AND" )
      fmla.right = convertToBoolean( rightGoal )

    elif len( leftGoals ) < 1 :
      fmla.unary = convertToBoolean( rightGoal )

    else : # leftGoals contains only one goal
      fmla.left  = convertToBoolean( leftGoals[0] )
      fmla.right = convertToBoolean( rightGoal )

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


###########
#  MERGE  #
###########
def merge( subfmlas, op ) :

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
        fmla.left  = merge( subfmlas[:-1], op ) # subfmlas[:-1] is of type list
        fmla.right = merge( [ subfmlas[-1] ], op ) # subfmlas[-1] is of type BooleanFormula

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
def getLeftFmla( provTreeList, op ) :

  mergeFmla = None
  subfmlas = []

  for provTree in provTreeList :
    #displayTree( provTree )
    subfmlas.append( convertToBoolean( provTree ) )

  mergedFmla = merge( subfmlas, op )

  return mergedFmla


##################
#  DISPLAY TREE  #
##################
# input provenance tree
# display relevant info about the tree to stdout
# good for debugging
def displayTree( tree ) :
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
def checkDescendantTypes( provTree, targetType ) :

  descList = provTree.root.descendants

  for d in descList :
    if not d.treeType == targetType :
      return False

  return True



#########
#  EOF  #
#########
