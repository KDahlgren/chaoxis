#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

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
def bugFreeExecution( results, eot ) :

  # grab relevant tuple lists
  pre  = results[ "pre" ]
  post = results[ "post" ]

  # check if every tuple in pre at EOT
  # also appears in post at EOT
  for pretup in pre :

    # check if last element of post record is an integer
    try :
      val = int( pretup[-1] )
    except :
      tools.bp( __name__, inspect.stack()[0][3], " Could not convert last element of the pre record  " + str(pretup) + ", pretup[-1] = " + str(pretup[-1]) + " into an integer. Therefore, cannot compare with EOT." )

    if ( int( pretup[-1] ) == eot) and not pretup in post :
      return False

  return True
