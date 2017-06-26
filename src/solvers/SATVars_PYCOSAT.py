
# modified from https://github.com/palvaro/ldfi-py

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import pycosat
from types import *
import inspect, os, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# **************************************** #

DEBUG = tools.getConfig( "SOLVERS", "SATVARS_PYCOSAT_DEBUG", bool )

######################
#  SAT VARS PYCOSAT  #
######################
class SATVars_PYCOSAT :


  ################
  #  ATTRIBUTES  #
  ################
  var2num = None  # dictionary
  num2var = None  # dictionary
  counter = None  # int


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self ) :
    self.var2num    = {}
    self.num2var    = {}
    self.counter    = 1


  ################
  #  LOOKUP VAR  #
  ################
  # given a variable from a solution, return the integer id
  # after filtering non-clock facts and uninteresting clock facts to None.
  def lookupVar( self, var ) :

    if DEBUG :
      print "var = " + str( var )

    # check if variable already mapped in var2num
    if not self.var2num.has_key( var ) :

      currID = self.counter
  
      # assign the id
      if "_NOT_" in var : # negate id if it's a negative variable
        var                 = var.replace( "_NOT_", "" ) # cleaning hack for good aesthetics
        self.var2num[ var ] = int( -1 ) * currID
      else :
        self.var2num[ var ] = currID

      self.num2var[ currID ] = var
      self.counter          += 1

      return self.var2num[ var ] # return the list of nums corresponding to vars in the dic


  ################
  #  LOOKUP NUM  #
  ################
  # given integer id, return the assocated variable
  def lookupNum(self, num):
    if num < 0:
      return "NOT " + self.num2var[-num]
    else:
      return self.num2var[num]


#########
#  EOF  #
#########
