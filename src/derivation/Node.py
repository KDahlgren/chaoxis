#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

# **************************************** #

DEBUG = True

class Node( object ) :

  #############
  #  ATTRIBS  #
  #############
  treeType = None
  name     = None  # name of relation identifier
  record   = []
  bindings = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, treeType, name, record , bindings ) :
    self.treeType = treeType
    self.name     = name
    self.record   = record
    self.bindings = bindings

  ##############
  #  GET NAME  #
  ##############
  def getName( self ) :
    return self.name

  ##################
  #  GET BINDINGS  #
  ##################
  def getBindings( self ) :
    return self.bindings
