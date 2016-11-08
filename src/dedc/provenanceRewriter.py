#!/usr/bin/env python

'''
provenanceRewriter.py
   Define the functionality for adding provenance rules
   to the datalog program.
'''

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

#from utils import tools, parseCommandLineInput
# ------------------------------------------------------ #

##############
#  AGG PROV  #
##############
def aggRuleProv( cursor ) :
  return None

#######################
#  REGULAR RULE PROV  #
#######################
def getProv( cursor ) :
  return None

########################
#  REWRITE PROVENANCE  #
########################
def rewriteProvenance( ruleMeta, cursor ) :
  return None

#########
#  EOF  #
#########
