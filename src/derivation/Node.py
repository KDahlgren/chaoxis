#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #

DEBUG = False

class Node( object ) :

  #############
  #  ATTRIBS  #
  #############
  treeType = None
  name     = None  # name of relation identifier
  isNeg    = None
  record   = []
  results  = None
  cursor   = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, treeType, name, isNeg, record, results, cursor ) :
    self.treeType = treeType
    self.name     = name
    self.isNeg    = isNeg
    self.record   = record
    self.results  = results
    self.cursor   = cursor


#########
#  EOF  #
#########
