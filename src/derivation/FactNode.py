#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# **************************************** #

DEBUG = True

class FactNode( ) :

  #############
  #  ATTRIBS  #
  #############
  treeType  = "fact"
  name      = None  # name of relation identifier
  isNeg     = False # is goal negative? assume positive
  record    = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, n, i, r ) :
    self.name   = n
    self.isNeg  = i
    self.record = r

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

  ##############
  #  GET NAME  #
  ##############
  def getName( self ) :
    return self.name

  ##############
  #  GET SIGN  #
  ##############
  def getSign( self ) :
    return self.isNeg

  ################
  #  GET RECORD  #
  ################
  def getRecord( self ) :
    return self.record

  ################
  #  PRINT NODE  #
  ################
  def printNode( self ) :
    print "FACT NODE: name = " + self.name + " ; isNeg = " + self.isNeg + " ; record = " + self.record


#########
#  EOF  #
#########
