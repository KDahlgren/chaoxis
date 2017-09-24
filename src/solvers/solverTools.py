#!/usr/bin/env python

'''
solverTools.py
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
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utilities import tools

# **************************************** #

DEBUG = False
#DEBUG = tools.getConfig( "SOLVERS", "SOLVERTOOLS_DEBUG", bool )


###############
#  SOLVE CNF  #
###############
def solveCNF( solverType ) :

  solvers = [ "PYCOSAT" ]

  # create a PYCOSAT solver instance
  if solverType == solvers[0] :
    return Solver_PYCOSAT.Solver_PYCOSAT( "PYCOSAT" )

  # WHAAAAA???
  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized solver type '" + solverType + "', currently recognized solvers are : " + str(solvers) )


###################
#  GET CONJUNCTS  #
###################
# return list of lists of disjunctive variables
def getConjuncts( cnfFormula_str ) :

  print
  print "cnfFormula_str = " + str( cnfFormula_str )
  print

  # split on ANDs
  cnfFormula_str = cnfFormula_str.replace( "AND", "__AND__" )
  cnfFormula_str = cnfFormula_str.replace( "OR" , "__OR__"  )
  cnfFormula_str = "".join( cnfFormula_str.split() )             # remove whitespace
  cnfFormula_str = cnfFormula_str.replace( "__OR__" , " OR "  )  # to align with pycosat formatting
  clauses = cnfFormula_str.split( "__AND__" )                    # divide clauses by the ANDs

  # clean strs
  cleanClauses = []
  for c in clauses :
    if DEBUG :
      print "c = " + str( c )
    c = c.replace( "([", "__OPENPARENBRA__" )
    c = c.replace( "])", "__CLOSBRAPAREN__" )
    c = c.replace( ",", "__COMMA__" )
    c = c.replace( "(", "" )
    c = c.replace( ")", "" )
    cleanClauses.append( c )

  if DEBUG :
    print "cleanClauses = " + str( cleanClauses )

  masterList = []
  # for clause in resulting list, collect a list of constituent vars
  # and add to master list.
  for c in cleanClauses :
    c = c.split( " OR " )
    masterList.append( c )

  if DEBUG :
    print "masterList = " + str( masterList )

  return masterList # needs to be a list of lists b/c using a map in Solver_PYCOSAT


####################
#  CONVERT TO CNF  #
####################
# convert a raw boolean formula to cnf, if possible,
# using sympy.
def convertToCNF( rawBooleanFmla_string ) :

  cnfFmla = None

  print "rawBooleanFmla_string"
  print rawBooleanFmla_string

  # transform booleanFmla into the sympy format
  sympy_info = format_sympy( rawBooleanFmla_string ) # returns tuple of ( sympy formula string, symbol string )

  print "sympy_infor"
  print sympy_info

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
    #   ([  --->  __OPENPARENBRA__
    #   ])  --->  __CLOSBRAPAREN__
    #   ,  --->  __COMMA__
    tmp = dirtyStr
    tmp = tmp.replace( "'", "" )
    tmp = tmp.replace( '"', "" )
    tmp = tmp.replace( "([", "__OPENPARENBRA__" )
    tmp = tmp.replace( "])", "__CLOSBRAPAREN__" )
    tmp = tmp.replace( ",", "__COMMA__" )
    #tmp = tmp.replace( "goal->", "goal__ARROW__" )
    tmp = tmp.replace( "goal->", "" )
    cleanResult = tmp

  elif newFormat == "legible" :
    # transform back into legible syntax
    cleanResult = dirtyStr
    cleanResult = cleanResult.replace( "__OPENPARENBRA__", "([" )
    cleanResult = cleanResult.replace( "__CLOSBRAPAREN__", "])" )
    cleanResult = cleanResult.replace( "__COMMA__"  , "," )
    #cleanResult = cleanResult.replace( "goal__ARROW__","goal->" )
    cleanResult = cleanResult

  else :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: unrecognized format requested: " + str( newFormat ) )

  return cleanResult


##################
#  FORMAT SYMPY  #
##################
# replace all 'AND's with & and all 'OR's with | and all '_NOT_''s with ~
def format_sympy( rawBooleanFmla ) :

  # return data
  sympy_expr        = None # type string
  sympy_symbol_list = None # type string

  cleanFmla = toggle_format_str( rawBooleanFmla, "valid_vars" )

  print "cleanFmla :"
  print cleanFmla

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

  #tools.bp( __name__, inspect.stack()[0][3], "sympy_fmla = " + str(sympy_fmla) )

  # NOT the CNF formula because LDFI is interested in the set of variable 
  #   assignments which render the original formula false.
  #   Therefore, need solutions for making !origfmla _true_.
  sympy_fmla = "~(" + sympy_fmla + ")"
  #sympy_fmla = sympy_fmla # not doing the last NOT

  print "sympy_fmla"
  print sympy_fmla

  print "Generating cnf formula..."
  result = sympy.to_cnf( sympy_fmla, simplify=False )
  #result = sympy.to_cnf( sympy_fmla, simplify=True  ) # SLOW! even on simplelog (>.<)'
  print "...done generating cnf formula."

  # WARNING: sympy (rather sillily imo) overrides "replace" for Basic types.
  # bypassing with a format toggling function...
  result_str = toggle_format_str( str( result ), "legible" )

  print "result_str :"
  print result_str

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
  tmp3 = tmp2.replace( "~", "_NOT_" )

  fmla_std = tmp3

  return fmla_std


#########
#  EOF  #
#########
