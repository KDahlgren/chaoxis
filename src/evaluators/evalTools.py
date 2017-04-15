#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys
from types import *

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools

# **************************************** #

DEBUG = True


####################
#  CHECK FOR BUGS  #
####################
# check if the pre -> post
# specifically, the condition is true if the 
# evaluation results satisfy the following statement:
#
# if a tuple t exists in the pre relation upon evaluation,
# then t exists in the post relation upon evaluation.
#
# In other words, the set of tuples in post is a superset
# of the set of tuples in pre.
#
# assume right-most attribute/variable/field value 
# in both pre and post represents delivery time.
def bugConditions( results, eot ) :

  # ------------------------------------------------------------------------------ #
  # sanity check pre and post must appear in the evaluation results.
  if not "pre" in results :
    dedt.cleanUp( irCursor, saveDB )
    tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining pre" )
  elif not "post" in results :
    dedt.cleanUp( irCursor, saveDB )
    tools.bp( __name__, inspect.stack()[0][3], "ERROR : no rule defining post" )
  # ------------------------------------------------------------------------------ #

  isBugFree   = True   # be optimistic ~(^.^)~
  explanation = None

  # grab relevant tuple lists
  pre  = results[ "pre" ]
  post = results[ "post" ]

  if DEBUG :
    print " eot = " + str( eot )
    print " pre = " + str( pre )
    print "post = " + str( post ) 

  # ------------------------------------------------------- #
  # CHECK #0 : if pre == post == empty, then program is bug free.
  if pre == [] and post == [] :
    isBugFree   = True
    explanation = "No tuples in pre and no tuples in post."

  # ------------------------------------------------------- #
  # CHECK #1 : all eot tups in pre must exist in post
  for pretup in pre :
    if ( int( pretup[-1] ) == eot ) and not pretup in post :
      isBugFree   = False
      explanation = "eot tuples exist in pre, but not in post"

  # ------------------------------------------------------- #
  # CHECK #2 : pre and post must have eot tuples
  if noEOT( pre, eot ) and noEOT( post, eot ) :
    isBugFree = False
    explanation = "no eot tuples in pre and no eot tuples in post."

  return [ isBugFree, explanation ]


############
#  NO EOT  #
############
# check if the input table contains any eot tuples.
# assumes send time placed in the rightmost field.
def noEOT( tableResults, eot ) :

  noEOTTuple = False

  for row in tableResults :
    if int(row[-1]) == int(eot) : # gawd! sometimes weak typing sucks....
      noEOTTuple = True

  return noEOTTuple



#########
#  EOF  #
#########
