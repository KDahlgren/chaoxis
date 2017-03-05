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


########################
#  CHECK FOR EVAL BUG  #
########################
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
def bugFreeExecution( results, eot, executionStatus ) :

  isBugFree   = True   # be optimistic ^.^
  explanation = None

  # grab relevant tuple lists
  pre  = results[ "pre" ]
  post = results[ "post" ]

  print " eot = " + str( eot )
  print " pre = " + str( pre )
  print "post = " + str( post ) 

  # ------------------------------------------------------- #
  # CHECK #0 :  
  #   check if last elements of all pre record are integers
  for pretup in pre :
    try :
      val = int( pretup[-1] )
    except :
      tools.bp( __name__, inspect.stack()[0][3], " Could not convert last element of the pre record  " + str(pretup) + ", pretup[-1] = " + str(pretup[-1]) + " into an integer. Therefore, cannot compare with EOT." )

  # ------------------------------------------------------- #
  # CHECK #1 :  
  #   check if last elements of all pre record are integers
  for posttup in post :
    try :
      val = int( posttup[-1] )
    except :
      tools.bp( __name__, inspect.stack()[0][3], " Could not convert last element of the post record  " + str(posttup) + ", posttup[-1] = " + str(posttup[-1]) + " into an integer. Therefore, cannot compare with EOT." )

  # ------------------------------------------------------- #
  # CHECK #2 : only interested in tuples occuring at eot
  eotTupsExist = False # glass half empty
  for posttup in post :
    if int( posttup[-1] ) == eot :
      eotTupsExist = True

  if not eotTupsExist :
    isBugFree   = False
    explanation = "post contains no eot data"

  # ------------------------------------------------------- #
  # CHECK #3 : all eot tups in pre must exist in post
  for pretup in pre :
    if ( int( pretup[-1] ) == eot ) and not pretup in post :
      isBugFree   = False
      explanation = "eot tuples exist in pre, but not in post"

  # ------------------------------------------------------- #
  # CHECK #4 : no more eot tuples in post
  if executionStatus == "noMoreEOTPostRecords" :
    isBugFree   = False
    explanation = "noMoreEOTPostRecords"

  # ------------------------------------------------------- #
  # CHECK #5 : exhausted all clock-only solutions
  #   this means post satisfies pre, despite turning off
  #   the discovered combinations of clock solutions.
  if executionStatus == "exhaustedClockOnlySolns" :
    isBugFree   = True
    explanation = "exhaustedClockOnlySolns"
 
  # ------------------------------------------------------- #

  return [ isBugFree, explanation ]


#########
#  EOF  #
#########
