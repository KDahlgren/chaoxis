#/usr/bin/env python

import os, sys

from ctypes import *
lib = cdll.LoadLibrary('../../../lib/c4/build/src/libc4/libc4.dylib')

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
      fo = open( filename, "r" )
      program = fo.readline()
      fo.close()
      return program

    except IOError :
      print "Could not open file " + filename
      return None

  #########
  #  RUN  #
  #########
  # fullprog is a string of concatenated overlog commands.
  # clockFactList = list of complete clocl fact commands in overlog.
  def run( self, fullprog, clockFactList ) :
    lib.c4_initialize()
    self.c4_obj = lib.c4_make( None, 0 )

    # ---------------------------------------- #
    # loading program
    if C4_WRAPPER_DEBUG :
      print "... loading prog ..."

    c_prog = bytes(fullprog)
    #lib.c4_install_str( self.c4_obj, c_prog )

    # ---------------------------------------- #
    # loading clock facts
    if C4_WRAPPER_DEBUG :
      print "... loading clock facts ..."

    for f in clockFactList : #adding clock facts separately to mimic time delay.
      if C4_WRAPPER_DEBUG :
        print "Clock fact = " + str( f )

      c_str_fact = None
      #lib.c4_install_str( self.c4_obj, c_str_fact )

    # ---------------------------------------- #
    # dump program results

    # ---------------------------------------- #
    # close prog
    if C4_WRAPPER_DEBUG :
      print "... closing C4 ..."

    lib.c4_destroy( self.c4_obj )
    #lib.c4_terminate( )

    # ---------------------------------------- #
    return None


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
print "[ Executing C4 wrapper ]"
w              = C4Wrapper() # initializes c4
filename       = "/Users/KsComp/projects/pyldfi/src/evaluators/programFiles/c4program.olg"

progFull       = w.getInputProg_file( filename )
clockFactList  = []

if C4_WRAPPER_DEBUG :
  print "Program = \n" + str( progFull )
  print "clock facts list = \n" + str(clockFactList)

w.run( progFull, clockFactList)

#########
#  EOF  #
#########
