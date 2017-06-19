
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
  def __init__(self):
    self.var2num = {}
    self.num2var = {}
    self.counter = 1


  ######################
  #  NOT A CLOCK FACT  #
  ######################
  def notAClockFact( self, var ) :
    if not "clock__OPENPAR____OPENBRA__" in var :
      return True
    else :
      return False


  ##################
  #  IS SELF COMM  #
  ##################
  def isSelfComm( self, var ) :
    fact = self.getClockVarContents( var )
    if fact[0] == fact[1] :
      return True
    else :
      return False


  ##############
  #  IS CRASH  #
  ##############
  def isCrash( self, var ) :
    fact = self.getClockVarContents( var )
    if fact[1] == "_" :
      return True
    else :
      return False


  ############################
  #  GET CLOCK VAR CONTENTS  #
  ############################
  def getClockVarContents( self, var ) :
    # isolate the first and second components of the clock fact
    fact = var.split( "__OPENPAR____OPENBRA__" )
    fact = fact[-1]
    fact = fact.replace( "__CLOSBRA____CLOSPAR__", "" )
    fact = fact.split( "__COMMA__" ) # the complete tuple as an array [ src, dest, sndTime, delivTime ]
    return fact


  ################
  #  LOOKUP VAR  #
  ################
  # given variable, return the integer id
  def lookupVar(self, var) :
    if DEBUG :
      print "var = " + str( var )

    # check if variable already mapped in var2num
    if not self.var2num.has_key( var ) :

      # --------------------------------------------------- #
      # filter out non-clock facts
      # remove non clock facts from fmla
      if self.notAClockFact( var ) :
        return None

      # --------------------------------------------------- #
      # filter out uninteresting clock facts
      # remove self comms
      elif self.isSelfComm( var ) :
        return None

      # remove crashes
      elif self.isCrash( var ) :
        return None

      # --------------------------------------------------- #
      # this is an interesting clock fact
      else :
        currID = self.counter

        # assign the id
        if "NOT" in var : # negate id if it's a negative variable
          var                 = var.replace( "_NOT_", "" ) # cleaning hack for good aesthetics
          self.var2num[ var ] = int( -1 ) * currID
        else :
          self.var2num[ var ] = currID

        self.num2var[ currID ] = var
        self.counter += 1

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
