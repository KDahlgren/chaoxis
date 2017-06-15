#!/usr/bin/env python

'''
settings.py
  Set globals throughout the PyLDFI code.
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utils import tools

# **************************************** #


##############
#  SETTINGS  #
##############
# path_to_settings_file is provided by the user at the command line.
def settings( path_to_settings_file ) :

  if os.path.isfile( path_to_settings_file ) : 
    print "USING settings file at  " + path_to_settings_file
    settings_driver( path_to_settings_file )

  else :
    print "WARNING : no settings file detected at " + path_to_settings_file


#####################
#  SETTINGS DRIVER  #
#####################
def settings_driver( path_to_settings_file ) :

  # get file contents
  lines = []
  f = open( path_to_settings_file )
  for line in f :
    line = "".join( line.split() ) # remove all whitespace
    if not line == "" :
      lines.append( line )
  f.close()

  print "USING settings : " + str( lines )

  for line in lines :

    line = line.split( '=' )
    if not line[1] == "True" and not line[1] == "False" :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : the rhs of settings must be True or False" )

    # ---------------------------- #
    #  CHECK FOR DEBUG STATEMENTS  #
    # ---------------------------- #
    res = checkDebugs( line )

    if not res :
      # --------------------------#
      #  CHECK FOR OTHER CONFIGS  #
      # --------------------------#
      checkConfigs( line )

  print "done loading settings."


##################
#  CHECK DEBUGS  #
##################
def checkDebugs( line ) :

  param = line[0]
  if line[1] == "True" :
    arg = True
  else :
    arg = False

  # assume line is a debug setting
  res = True

  if "ALL_DEBUG" == param :
    all_debug( arg )

  elif "LDFICORE_DEBUG" == param :
    ldficore_settings( arg, None, None, None )

  # otherwise, line is not a debug setting
  else :
    res = False

  return res


###################
#  CHECK CONFIGS  #
###################
def checkConfigs( line ) :

  param = line[0]
  if line[1] == "True" :
    arg = True
  else :
    arg = False

  if "PROV_TREES_ON" == param :
    ldficore_settings( None, arg, None, None )

  elif "OUTPUT_PROV_TREES_ON" == param :
    ldficore_settings( None, None, arg, None )

  elif "OUTPUT_TREE_CNF_ON" == param :
    ldficore_settings( None, None, None, arg )

  # otherwise, line does not specify a known debug or config parameter
  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unknown settings parameter in " + str( line ) )


###############
#  ALL DEBUG  #
###############
def all_debug( arg ) :
  return None


#######################
#  LDFICORE SETTINGS  #
#######################
def ldficore_settings( debug, prov_trees_on, output_prov_trees_on, output_tree_cnf_on ) :
  return None

#########
#  EOF  #
#########
