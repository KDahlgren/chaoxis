#!/usr/bin/env python

'''
tools.py
   A storage location for generally applicable methods used to
   sanity-check particular properties.
'''

import os, random, sys

############
#  GET ID  #
############
# input nothing
# output random 16 char alphanumeric id
def getID() :
  return "".join( random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16) )

#######################
#  CHECK PARENTHESES  #
#######################
def checkParentheses( line ) :
  numOpen   = 0 # number of open parentheses "("
  numClosed = 0 # number of closed parentheses ")"

  for c in line :
    if c == "(" :
      numOpen += 1
    elif c == ")" :
      numClosed += 1

  if not numOpen == numClosed :
    sys.exit( "ERROR: Incorrect number of parentheses in line: " + line )

  return True

#########
#  EOF  #
######### 
