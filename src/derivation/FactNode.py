#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

packagePath1  = os.path.abspath( __file__ + "/.." )
sys.path.append( packagePath1 )
from Node import Node

# **************************************** #

DEBUG = True

class FactNode( Node ) :

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record, results, cursor ) :
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "fact", name, isNeg, record, results, cursor )


  #############
  #  __STR__  #
  #############
  # the string representation of a FactNode
  def __str__( self ) :
    if self.isNeg :
      negStr = "_NOT_"
      return "fact-> " + negStr + " " + self.name + "(" + str(self.record) + ")"
    else :
      return "fact-> " + self.name + "(" + str(self.record) + ")"


  ##################
  #  FMLA DISPLAY  #
  ##################
  def fmlaDisplay( self ) :
    if self.isNeg :
      negStr = "_NOT_"
      return negStr + self.name + "(" + str(self.record) + ")"
    else :
      return self.name + "(" + str(self.record) + ")"

#########
#  EOF  #
#########
