#!/usr/bin/env python

'''
solverTools.py
  Tools for converting provenance trees into CNF
  formulas.
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils      import parseCommandLineInput, tools

# **************************************** #


#########
#  EOF  #
#########
