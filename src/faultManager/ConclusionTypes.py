#!/usr/bin/env python

'''
ConclusionTypes.py
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

import driverTools

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

# **************************************** #


DEBUG = False


class ConclusionTypes :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  categories = []

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self ) :

    self.categories.append( "NoCounterexampleFound" )
    self.categories.append( "FoundCounterexample" )


#########
#  EOF  #
#########
