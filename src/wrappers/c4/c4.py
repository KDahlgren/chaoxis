#!/usr/bin/env python

import os, sys

from ctypes import cdll
lib = cdll.LoadLibrary('../../../lib/c4/build/src/libc4/libc4.dylib')

class C4Wrapper( object ) :

  #############
  #  ATTRIBS  #
  #############
  c4_obj = None    # the target c4 program object 

  ##########
  #  INIT  #
  ##########
  def __init__( self ) :
    lib.c4_initialize()
    self.c4_obj = lib.c4_make( None, 0 )

  #########################
  #  GET INPUT LIST FILE  #
  #########################
  def getInputList_file( self, filename ) :
    print "Importing program from " + filename

    try :
      fo = open( filename, "r" )
      program = fo.readline()
      listProgram = program.split(";")

      print "Program :" + "\n" #+ program
      prog = []
      for l in listProgram :
        print l + " ;"
        prog.append( l + " ;" )

      return prog

    except IOError :
      print "Could not open file " + filename
      return None

  #########################
  #  GET INPUT PROG FILE  #
  #########################
  def getInputProg_file( self, filename ) :
    print "Importing program from " + filename

    try :
      fo = open( filename, "r" )
      program = fo.readline()
      return program

    except IOError :
      print "Could not open file " + filename
      return None

  #####################
  #  LOAD PROG LINES  #
  #####################
  def loadProgLines( self, progLineList ) :
    print "... running c4_loadProgLines ..."

    for line in progLineList :
      print "line = " + line
      lib.c4_install_str( self.c4_obj, line )

  ###############
  #  LOAD PROG  #
  ###############
  def loadProg( self, prog ) :
    print "... running c4_loadProg ..."
    lib.c4_install_str( self.c4_obj, prog )

  ################
  #  CLOSE PROG  #
  ################
  def closeProg( self ) :
    print "... running closeProg ..."
    #lib.c4_destroy( self.c4_obj )
    #lib.c4_terminate( )    # terminate runs without seg faulting. \(^.^)/


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
print "[ Executing C4 wrapper ]"
w         = C4Wrapper() # initializes c4
filename  = "/Users/KsComp/projects/pyldfi/src/evaluators/programFiles/c4program.olg"
progList  = w.getInputList_file( filename )
progList1 = progList[:len(progList)-1]
print progList1
#w.loadProgLines( progList1 )

progFull = w.getInputProg_file( filename )
print progFull
w.loadProg( progFull )
w.closeProg()

#########
#  EOF  #
#########
