#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# **************************************** #

DEBUG = True

class Node( object ) :

  #############
  #  ATTRIBS  #
  #############
  treeType       = None
  name           = None  # name of relation identifier
  record         = []
  bindings       = []
  schema         = []
  schemaBindings = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, treeType, name, record , bindings, cursor ) :
    self.treeType = treeType
    self.name     = name
    self.record   = record
    self.bindings = bindings
    self.schema   = self.setSchema( name, cursor )

  ################
  #  SET SCHEMA  #
  ################
  def setSchema( self, rname, cursor ) :
    schema = []

    nameList = self.getNameList( rname, cursor )

    for i in range(0,len(nameList)) :
      name = nameList[i]
      # case fact
      if self.treeType == "fact" :
        cursor.execute( "SELECT attID,attName FROM Fact,FactAtt WHERE name=='" + name + "' AND Fact.fid==FactAtt.fid" )
        schema_db = cursor.fetchall()
        schema_db = tools.toAscii_multiList( schema_db )
      # case rule or goal
      else :
        cursor.execute( "SELECT attID,attName FROM Rule,GoalAtt WHERE goalName=='" + name + "' AND Rule.rid==GoalAtt.rid" )
        schema_db = cursor.fetchall()
        schema_db = tools.toAscii_multiList( schema_db )

      schema_db = self.cleanSchema( schema_db )
      schema_db = list( set( schema_db ) ) # ??? why needed ???

      if i == 0 :
        schema.extend( schema_db )
      #elif not len(schema) == len(schema_db) :
      #  sys.exit( "ERROR: rule " + name + " possesses different numbers of attributes per associated rule definition.\nschema = " + str(schema) + "\nschema_db = " + str(schema_db) )
      else :
        schema = self.mergeElements( schema, schema_db )

    return schema


  ####################
  #  MERGE ELEMENTS  #
  ####################
  def mergeElements( self, schema1, schema2 ) :
    retSchema = []
    if not len( schema1 ) == len( schema2 ) :
      if len( schema1 ) > len( schema2 ) :
        retSchema.extend( schema1 )
        for j in range(0,len(schema2)) :
          retSchema[j] = retSchema[j] + "/" + schema2[j]

      else :
        retSchema.extend( schema2 )
        for j in range(0,len(schema1)) :
          retSchema[j] = retSchema[j] + "/" + schema1[j]

    return retSchema

  ###################
  #  GET NAME LIST  #
  ###################
  def getNameList( self, rname, cursor ) :
    cursor.execute( "SELECT goalName FROM Rule" )
    temp = cursor.fetchall()
    temp = tools.toAscii_multiList( temp )
    nameList = []
    for n in temp :
      name = n[0]
      if not "_prov" in rname :
        if rname == name :
          nameList.append( name )
      else :
        if name.startswith( rname ) :
          nameList.append( name )
    return nameList

  ##################
  #  CLEAN SCHEMA  #
  ##################
  def cleanSchema( self, schema ) :
    cleanSchema = []
    for arr in schema :
      cleanSchema.append( arr[1] )
    return cleanSchema
