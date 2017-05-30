#/usr/bin/env python

#############
#  IMPORTS  #
#############
# standard python packages
import pycosat
from types import *
from ctypes import *
import inspect, itertools, os, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils   import tools
# **************************************** #

DEBUG = False

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
    if DEBUG :
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


  #############################
  #  GET INPUT PROG LIST ALL  #
  #############################
  def getInputProg_list_all_clocks( self, filename ) :
    if DEBUG :
      print "Importing program from " + filename

    try :
      program = []
      fo = open( filename, "r" )
      for line in fo :
        line = line.rstrip()
        program.append( line )
      fo.close()

      codeStatementsOnly = "" # string of code statements only. no clock statements.
      clockStatements    = [] # list of strings grouping clock statements by SndTime
      currClockList      = ""
      currTime           = 1

      # only works if clock facts are sorted by increasing SndTime when 
      # appearing in the input c4 file.
      # also only works if simulations start at time 1.
      for i in range(0 ,len(program)) :

        statement       = program[i]
        parsedStatement = statement.split( "(" )

        # CASE : hit a clock fact
        if parsedStatement[0] == "clock" :
          clockStatements.append( statement ) # save the old clock group

        # CASE : hit a non clock fact
        else :
          codeStatementsOnly += statement

      finalProg = [ codeStatementsOnly ]
      finalProg.extend( clockStatements )
      return finalProg

    except IOError :
      print "Could not open file " + filename
      return None


  ######################################
  #  GET INPUT PROG FILE GROUP CLOCKS  #
  ######################################
  def getInputProg_group_clocks( self, filename ) :
    if DEBUG :
      print "Importing program from " + filename

    try :
      program = []
      fo = open( filename, "r" )
      for line in fo :
        line = line.rstrip()
        program.append( line )
      fo.close()

      codeStatementsOnly   = "" # string of code statements only. no clock statements.
      clockStatementGroups = [] # list of strings grouping clock statements by SndTime
      currClockList        = ""
      currTime             = 1

      # only works if clock facts are sorted by increasing SndTime when 
      # appearing in the input c4 file.
      # also only works if simulations start at time 1.
      for i in range(0 ,len(program)) :

        statement = program[i]
        nextStatement = None
        lastClock     = False

        parsedStatement = statement.split( "(" )

        # CASE : hit a clock fact
        if parsedStatement[0] == "clock" :

          # check if the next statement in the program also declares a clock fact
          try :
            nextStatement    = program[ i+1 ]
            parsedStatement1 = nextStatement.split( "(" )
            parsedClockArgs1 = parsedStatement1[1].split( "," ) # split clock fact arguments into a list
            assert( parsedStatement1[0] == "clock" )
          except :
            lastClock = True

          parsedClockArgs = parsedStatement[1].split( "," ) # split clock fact arguments into a list

          # check if SndTime is in the current group
          if not lastClock and int( parsedClockArgs[2] ) == currTime :
            currClockList += statement

          # hit a clock fact in the next time group
          elif not lastClock and int( parsedClockArgs[2] ) > currTime :
            clockStatementGroups.append( currClockList ) # save the old clock group
            currClockList  = ""                          # reset the clock group
            currClockList += statement                   # reset the clock group
            currTime       = int( parsedClockArgs[2] )   # reset the curr time

          # hit a clock fact in the last time group
          elif lastClock :
            clockStatementGroups.append( currClockList ) # save the old clock group

        # CASE : hit a non clock fact
        else :
          codeStatementsOnly += statement

      finalProg = [ codeStatementsOnly ]
      finalProg.extend( clockStatementGroups )
      return finalProg

    except IOError :
      print "Could not open file " + filename
      return None


  #########
  #  RUN  #
  #########
  # fullprog is a string of concatenated overlog commands.
  def run( self, fullprog_path, table_path, savepath ) :

    #fullprog  = self.getInputProg_file( fullprog_path )
    #fullprog  = self.getInputProg_group_clocks( fullprog_path )
    fullprog  = self.getInputProg_list_all_clocks( fullprog_path )
    tableList = self.getTableList( table_path )

    self.lib.c4_initialize()
    self.c4_obj = self.lib.c4_make( None, 0 )

    # ---------------------------------------- #
    # loading program
    if DEBUG :
      print "... loading prog ..."

    #c_prog = bytes( fullprog )
    #self.lib.c4_install_str( self.c4_obj, c_prog )

    for subprog in fullprog :
      c_prog = bytes( subprog )
      self.lib.c4_install_str( self.c4_obj, c_prog )

    # ---------------------------------------- #
    # dump program results to file
    if DEBUG :
      print "... dumping program ..."

    self.saveC4Results( tableList, savepath )

    # ---------------------------------------- #
    # close c4 program
    if DEBUG :
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
      if DEBUG :
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
