#!/usr/bin/env python

'''
Fact.py
   Defines the Fact class.
   Establishes all relevant attributes and get/set methods.
'''

import inspect, os, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import tools
# ------------------------------------------------------ #

DEBUG = False

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

  # get ordered attribute list
  def getAttList( self ) :
    self.cursor.execute( "SELECT attName,attID FROM FactAtt WHERE fid = '" + self.fid + "'" )
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
    attID       = 0  # allows duplicate attributes in attList
    defaultType = "UNDEFINED"
    for attName in attList :
      self.cursor.execute("INSERT INTO FactAtt VALUES ('" + self.fid + "','" + str(attID) + "','" + attName + "','" + str(defaultType) + "')")
      attID += 1


  ###################
  #  SET ATT TYPES  #
  ###################
  # set the types for fact contents
  def setAttTypes( self ) :
    allDataList = self.getAttList()               # ordered by appearance in program
    allAttTypes = self.getTypeList( allDataList ) # ordered by appearance in program

    # set att types for this fact
    # ordering is crucial
    attID = 0
    for attType in allAttTypes  :
      self.cursor.execute( "UPDATE FactAtt SET attType=='" + attType + "' WHERE fid=='" + self.fid + "' AND attID==" + str(attID) )
      attID += 1

    # dump table for debugging
    if DEBUG :
      self.cursor.execute( "SELECT * FROM FactAtt" )
      res = self.cursor.fetchall()
      res = tools.toAscii_multiList( res )
      print "FACT :"
      print self.display()
      print "CONTENTS OF TABLE FactAtt"
      for r in res :
        print r

      #tools.bp( __name__, inspect.stack()[0][3], "breaking here.wehjrb23khkbsadf" )


  ###################
  #  GET TYPE LIST  #
  ###################
  # return the ordered type list for all data in a fact
  def getTypeList( self, allDataList ) :

    typeList = []

    for data in allDataList :
      if "'" in data or '"' in data :
        typeList.append( "string" )
      elif data.isdigit() :
        typeList.append( "int" )
      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : Fact " + self.display() + " contains a datum of unrecognized type.\npyLDFI currently only recognizes strings surrounded by either double or single quotes and integers.\nAborting..." )

    return typeList


  # ------------------------------------- #
  #              DISPLAY                  #

  # print fact to stdout
  def display( self ) :
    prettyFact = ""

    name    = self.getName()
    attList = self.getAttList()
    timeArg = self.getTimeArg()

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

    #print prettyFact

    return prettyFact

#########
#  EOF  #
#########
