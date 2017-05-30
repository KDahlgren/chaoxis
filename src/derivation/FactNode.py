#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

packagePath1  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath1 )
from Node import Node

packagePath2  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath2 )
from utils import tools

# **************************************** #

DEBUG = False

class FactNode( Node ) :

  ########################
  #  SPECIAL ATTRIBUTES  #
  ########################
  triggerRecord = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record, results, cursor ) :

    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "fact", name, isNeg, record, results, cursor )

    # get trigger record
    self.triggerRecord = self.extractTrigger()

    # check to make sure the record exists as a fact
    if not self.verifyTriggerRecord() :
      print ">>> WARNING! triggerRecord " + str( record ) + " does not exist in the results: " + str( results ) + "\nCreating FactNode anyway..."
    #  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : self.triggerRecord = " + str(self.triggerRecord) + " is not a fact in the '" + str(self.name) + "' table results:\n" + str(self.results[self.name]) )


  #############
  #  __STR__  #
  #############
  # the string representation of a FactNode
  def __str__( self ) :
    if self.isNeg :
      negStr = "_NOT_"
      return "fact-> " + negStr + " " + self.name + "(" + str(self.triggerRecord) + ")"
    else :
      return "fact-> " + self.name + "(" + str(self.triggerRecord) + ")"


  #####################
  #  EXTRACT TRIGGER  #
  #####################
  # assume attributes added to the definitions of rules maifesting facts 
  # are added to the left of the list of existing original attributes
  # contributing to the definition of the fact schema.
  # Accordingly, the original fact constitutes the leftmost data items
  # of the seed record up to the arity of the original fact schema.
  def extractTrigger( self ) :

    # get arity of fact table results
    res = self.results[self.name]
    arity = len( res[0] )

    thisRec = self.record[ : arity ]
    thisRec = [ str(r) for r in thisRec ]  # transform all data items to strings to avoid migraines.

    return thisRec


  ###########################
  #  VERIFY TRIGGER RECORD  #
  ###########################
  def verifyTriggerRecord( self ) :

    if self.triggerRecord in self.results[ self.name ] :
      return True
    else :
      return False


#########
#  EOF  #
#########
