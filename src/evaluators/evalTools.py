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
def bugFreeExecution( results ) :

  # grab relevant tuple lists
  pre  = results[ "pre" ]
  post = results[ "post" ]

  # check if every tuple in pre
  # also appears in post
  for pretup in pre :
    if not pretup in post :
      return False

  return True
