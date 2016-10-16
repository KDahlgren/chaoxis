#!/usr/bin/env python

class Table() :
  # all tables are stored as an array of strings and arrays
  # instantiating the outermost table array
  table = []

  # type of table
  tableType = ""

  # constructor
  def __init__( self, typeOfTable ) :
    self.table     = []            # redundant, but good for clarity
    self.tableType = typeOfTable

  # all tables are accessible
  def getTable( self ) :
    return self.table

  # return type of table
  def getTableType( self ) :
    return self.tableType

  # all tables have an inesrt method
  def addRow( self, newRow ) :
    self.table.append( newRow )

  # all tables have a merge method
  def mergeTable( self, newTable ) :
    contents = newTable.getTable()
    self.table.extend( contents )
