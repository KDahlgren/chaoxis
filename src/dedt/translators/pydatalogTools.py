#!/usr/bin/env python

'''
pydatalog_translator.py
   Tools for producig pydatalog programs from the IR in the dedt compiler.
'''

import os, string, sqlite3, sys
import dumpers_pydatalog

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../../.." )
sys.path.append( packagePath )

from utils import dumpers, tools
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
PYDATALOG_TOOLS_DEBUG = True

#############
#  OPRULES  #
#############
def opRules( rule ) :
  return None
