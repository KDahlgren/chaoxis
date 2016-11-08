#!/usr/bin/env python

'''
Fact.py
   Defines the Fact class.
   Establishes all relevant attributes and get/set methods.
'''

import os, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# ------------------------------------------------------ #

class Fact :
  # attributes
  fid        = ""
  cursor     = None

  # constructor
  def __init__( self, fid, cursor ) :
    self.fid    = fid
    self.cursor = cursor

  # ------------------------------------- #
  #                GET                    #

  # get name
  def getName( self ) :
    self.cursor.execute( "SELECT name FROM Fact WHERE fid = '" + self.fid + "'" )
    nameList = self.cursor.fetchall()
    nameList = tools.toAscii_list( nameList )
    if not nameList == None :
      if len(nameList) == 1 :
        return nameList[0]
      else :
        sys.exit( "ERROR: Fact possesses more than 1 name: " + nameList )

  # get attribute list
  def getAttList( self ) :
    self.cursor.execute( "SELECT attName FROM FactAtt WHERE fid = '" + self.fid + "'" )
    attList = self.cursor.fetchall()
    attList = tools.toAscii_list( attList )
    return attList
  
  # get time argument
  def getTimeArg( self ) :
    self.cursor.execute( "SELECT timeArg FROM Fact WHERE fid = '" + self.fid + "'" )
    timeArgList = self.cursor.fetchall()
    timeArgList = tools.toAscii_list( timeArgList )
    if not timeArgList == None :
      if len(timeArgList) == 1 :
        return timeArgList[0]
      else :
        sys.exit( "ERROR: Fact possesses more than 1 timeArg: " + timeArgList )

  # ------------------------------------- #
  #                SET                    #

  # set fact name and time argument
  def setFactInfo( self, name, timeArg ) :
    self.cursor.execute("INSERT INTO Fact VALUES ('" + self.fid + "','" + name + "','" + timeArg + "')")

  # set attribute list
  def setAttList( self, attList ) :
    attID = 0  # allows duplicate attributes in attList
    for attName in attList :
      self.cursor.execute("INSERT INTO FactAtt VALUES ('" + self.fid + "','" + str(attID) + "','" + attName + "')")
      attID += 1

  # ------------------------------------- #
  #              DISPLAY                  #

  # print fact to stdout
  def display( self ) :
    prettyFact = ""

    name = self.getName()
    attList  = self.getAttList()
    timeArg  = self.getTimeArg()

    # convert fact info to pretty string
    prettyFact += name + "("

    for i in range( 0, len(attList) ) :
      if i < ( len(attList) - 1 ) :
        prettyFact += attList[i] + ","
      else :
        prettyFact += attList[i] + ")"

    if not timeArg == None :
      prettyFact += "@" + timeArg

    prettyFact += " ;" # end all facts with a semicolon

    print prettyFact


#########
#  EOF  #
#########
