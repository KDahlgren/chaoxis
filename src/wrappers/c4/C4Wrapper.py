#/usr/bin/env python

import os, sys

from ctypes import *
lib = cdll.LoadLibrary('../../../lib/c4/build/src/libc4/libc4.dylib')
lib.c4_make.restype       = POINTER(c_char)
lib.c4_dump_table.restype = c_char_p   # c4_dump_table returns a char*

C4_WRAPPER_DEBUG = True

class C4Wrapper( object ) :

  #############
  #  ATTRIBS  #
  #############
  wrapperID = None

  ##########
  #  INIT  #
  ##########
  def __init__( self ) :
    self.wrapperID = 0

  #########################
  #  GET INPUT PROG FILE  #
  #########################
  def getInputProg_file( self, filename ) :
    if C4_WRAPPER_DEBUG :
      print "Importing program from " + filename

    try :
      program = []
      fo = open( filename, "r" )
      for line in fo :
        print line
        line = line.rstrip()
        program.append( line )
      fo.close()

      return "".join( program )

    except IOError :
      print "Could not open file " + filename
      return None

  #########
  #  RUN  #
  #########
  # fullprog is a string of concatenated overlog commands.
  # clockFactList = list of clock facts in overlog format
  def run( self, fullprog, tableList ) :
    lib.c4_initialize()
    self.c4_obj = lib.c4_make( None, 0 )

    # ---------------------------------------- #
    # loading program
    if C4_WRAPPER_DEBUG :
      print "... loading prog ..."

    c_prog = bytes( fullprog )
    lib.c4_install_str( self.c4_obj, c_prog )

    # ---------------------------------------- #
    # dump program results
    if C4_WRAPPER_DEBUG :
      print "... dumping program ..."

      #print "---------------------------"
      #print "post"
      #print lib.c4_dump_table( self.c4_obj, "post" )

      #print "---------------------------"
      #print "a"
      #print lib.c4_dump_table( self.c4_obj, "a" )

      #print "---------------------------"
      #print "b"
      #print lib.c4_dump_table( self.c4_obj, "b" )

    for table in tableList :
      print "---------------------------"
      print table
      print lib.c4_dump_table( self.c4_obj, table )

    # ---------------------------------------- #
    # close prog
    if C4_WRAPPER_DEBUG :
      print "... closing C4 ..."

    lib.c4_destroy( self.c4_obj )
    lib.c4_terminate( )

    # ---------------------------------------- #
    return None


  ####################
  #  GET TABLE LIST  #
  ####################
  def getTableList( self, tableFile ) :
    fo = open( tableFile, "r" )
    line = fo.readline()
    line = line.rstrip()
    fo.close()
    return line.split( "," )


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == '__main__' :

  print "[ Executing C4 wrapper ]"
  w = C4Wrapper() # initializes c4

  # /////////////////////////////////// #
  filename   = "./myTest.olg"
  progFull   = w.getInputProg_file( filename )
  table_file = "./tableListStr.data"
  tableList  = w.getTableList( table_file )
  if C4_WRAPPER_DEBUG :
    print "Program  = \n" + str( progFull )
    print "tableStr = \n" + str( tableList )
  w.run( progFull, [ "a", "b", "post" ] )

  # /////////////////////////////////// #
  filename2   = "c4program.olg"
  prog2       = w.getInputProg_file( filename2 )
  table_file2 = "tableListStr.data"
  tableList2  = w.getTableList( table_file2 )
  if C4_WRAPPER_DEBUG :
    print "Program   = \n" + str( prog2 )
    print "tableList = \n" + str( tableList2 )
  w.run( prog2, tableList2 )


#########
#  EOF  #
#########
