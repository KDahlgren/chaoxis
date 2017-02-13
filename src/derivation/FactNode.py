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

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  isNeg    = False # is goal negative? assume positive

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, record , bindings, cursor ) :
    Node.__init__( self, "fact", name, record, bindings, cursor )
    self.isNeg    = isNeg

  ################
  #  PRINT TREE  #
  ################
  def printTree( self ) :
    print "********************************"
    print "           FACT NODE"
    print "********************************"
    print "name   :" + str( self.name   )
    print "isNeg  :" + str( self.isNeg  )
    print "record :" + str( self.record )

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    return "FACTNODE: " + str( self.name ) + "; \nisNeg " + str( self.isNeg ) + "; \nbindings = " + str( self.record )

  ##############
  #  GET SIGN  #
  ##############
  def getSign( self ) :
    return self.isNeg

#########
#  EOF  #
#########
