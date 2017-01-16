#/usr/bin/env python

import os, sys

from ctypes import cdll
lib = cdll.LoadLibrary('../../../lib/c4/build/src/libc4/libc4.dylib')

C4_WRAPPER_DEBUG = True

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
  #  GET INPUT PROG FILE  #
  #########################
  def getInputProg_file( self, filename ) :
    if C4_WRAPPER_DEBUG :
      print "Importing program from " + filename

    try :
      fo = open( filename, "r" )
      program = fo.readline()
      fo.close()
      return program

    except IOError :
      print "Could not open file " + filename
      return None

  ###############
  #  LOAD PROG  #
  ###############
  def loadProg( self, prog ) :
    if C4_WRAPPER_DEBUG :
      print "... running loadProg ..."
    lib.c4_install_str( self.c4_obj, prog )

  ######################
  #  LOAD CLOCK FACTS  #
  ######################
  def loadClockFacts( self, clockFactsList ) :
    if C4_WRAPPER_DEBUG :
      print "... running loadClockFacts ..."
    for f in clockFactsList : #adding clock facts separately to mimic time delay.
      if C4_WRAPPER_DEBUG :
        print "Clock fact = " + str( f )
      lib.c4_install_str( self.c4_obj, prog )

  ################
  #  CLOSE PROG  #
  ################
  def closeProg( self ) :
    if C4_WRAPPER_DEBUG :
      print "... running closeProg ..."
    lib.c4_destroy( self.c4_obj )
    lib.c4_terminate( )

    return None

##############################
#  MAIN THREAD OF EXECUTION  #
##############################
print "[ Executing C4 wrapper ]"
w              = C4Wrapper() # initializes c4
filename       = "/Users/KsComp/projects/pyldfi/src/evaluators/programFiles/c4program.olg"

progFull       = w.getInputProg_file( filename )
clockFactsList = []

if C4_WRAPPER_DEBUG :
  print "Program = \n" + str( progFull )
  print "clock facts list = \n" + str(clockFactsList)


#w.loadProg( progFull )
#w.loadClockFacts( clockFactsList )
#w.closeProg()

#########
#  EOF  #
#########
