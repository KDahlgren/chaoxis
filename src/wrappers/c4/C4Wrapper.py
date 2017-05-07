#/usr/bin/env python

import os, sys

from ctypes import *

C4_WRAPPER_DEBUG = False

class C4Wrapper( object ) :

  #############
  #  ATTRIBS  #
  #############
  #lib = cdll.LoadLibrary('../../../lib/c4/build/src/libc4/libc4.dylib')
  #lib                       = None
  #lib.c4_make.restype       = None
  #lib.c4_dump_table.restype = None

  ##########
  #  INIT  #
  ##########
  def __init__( self, c4_lib_loc ) :
    self.lib                       = cdll.LoadLibrary( c4_lib_loc )
    self.lib.c4_make.restype       = POINTER(c_char)
    self.lib.c4_dump_table.restype = c_char_p   # c4_dump_table returns a char*

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
  def run( self, fullprog_path, table_path, savepath ) :

    fullprog  = self.getInputProg_file( fullprog_path )
    tableList = self.getTableList( table_path )

    self.lib.c4_initialize()
    self.c4_obj = self.lib.c4_make( None, 0 )

    # ---------------------------------------- #
    # loading program
    if C4_WRAPPER_DEBUG :
      print "... loading prog ..."

    c_prog = bytes( fullprog )
    self.lib.c4_install_str( self.c4_obj, c_prog )

    # ---------------------------------------- #
    # dump program results to file
    if C4_WRAPPER_DEBUG :
      print "... dumping program ..."

    self.saveC4Results( tableList, savepath )

    # ---------------------------------------- #
    # close c4 program
    if C4_WRAPPER_DEBUG :
      print "... closing C4 ..."

    self.lib.c4_destroy( self.c4_obj )
    self.lib.c4_terminate( )

    # ---------------------------------------- #
    return None


  ####################
  #  GET TABLE LIST  #
  ####################
  # given a list of tables as a string, convert to list
  def getTableList( self, tableFile ) :
    fo = open( tableFile, "r" )
    line = fo.readline()
    line = line.rstrip()
    fo.close()
    return line.split( "," )


  #####################
  #  SAVE C4 RESULTS  #
  #####################
  # save c4 results to file
  def saveC4Results( self, tableList, savepath ) :

    # save new contents
    f = open( savepath, "w" )

    for table in tableList :
      
      # output to stdout
      if C4_WRAPPER_DEBUG :
        print "---------------------------"
        print table
        print self.lib.c4_dump_table( self.c4_obj, table )

      # output to file
      f.write( "---------------------------\n" )
      f.write( table + "\n" )
      f.write( self.lib.c4_dump_table( self.c4_obj, table ) )
      f.write( "\n" )

    f.close()

    return None


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == '__main__' :

  print "[ Executing C4 wrapper ]"
  w = C4Wrapper( '../../../lib/c4/build/src/libc4/libc4.dylib' ) # initializes c4

  # /////////////////////////////////// #
  prog1      = "./myTest.olg"
  table_file = "./tableListStr_myTest.data"
  w.run( prog1, table_file, "./myTest_save.txt" )

  # /////////////////////////////////// #
  prog2       = "c4program.olg"
  table_file2 = "tableListStr.data"
  w.run( prog2, table_file2, "./prog2_save.txt" )


#########
#  EOF  #
#########
