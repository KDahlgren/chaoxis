#!/usr/bin/env python

'''
e2e_tools.py
  Defines tools useful for the e2e unit tests.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import filecmp, inspect, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )
sys.path.append( os.path.abspath( __file__ + "/../../../../src/dedt" ) )

from dedt        import dedt
from translators import c4_translator
from utils       import tools

# ------------------------------------------------------ #


DEBUG = False


##########################
#  CMP DATALOG FILES C4  #
##########################
# input two files containing datalog
# determine whether the files specify the same program.
# return True if same program, False otherwise.
def cmpDatalogFiles_c4( file1, file2 ) :

  # get lines from file1
  fileLines_1 = []
  f1 = open( file1, "r" )
  for line in f1 :
    line = line.rstrip()
    fileLines_1.append( line )
  f1.close()

  # get lines from file2
  fileLines_2 = []
  f2 = open( file2, "r" )
  for line in f2 :
    line = line.rstrip()
    fileLines_2.append( line )
  f2.close()

  # CASE : different numbers of lines
  if not len( fileLines_1 ) == len( fileLines_2 ) :
    return False

  # CASE : file1 contains a line not in file2
  for line1 in fileLines_1 :
    noOccurence = True

    for line2 in fileLines_2 :

      if line1 == line2 : # lines are identical
        noOccurence = False

      # CASE : hit prov line, need to deal with random ids
      elif "_prov" in line1 and "_prov" in line2 :

        # prov defines
        if "define(" in line1 and "define(" in line2 :

          # grab relevant data from line1
          line1_list = line1.split( "_prov" )
          name1      = line1_list[0] + "_prov"
          remainder1 = line1_list[1]
          remainder1 = remainder1[16:]

          if DEBUG :
            print "line1      = " + str( line1 )
            print "name1      = " + str( name1 )
            print "remainder1 = " + str( remainder1 )

          # grab relevant data from line2
          line2_list = line2.split( "_prov" )
          name2      = line2_list[0] + "_prov"
          remainder2 = line2_list[1]
          remainder2 = remainder2[16:]

          if DEBUG :
            print "line2      = " + str( line2 )
            print "name2      = " + str( name2 )
            print "remainder2 = " + str( remainder2 )

          # identical names and remainders
          if (name1 == name2) and (remainder1 == remainder2) :
            noOccurence = False

        # CASE : hit a regular prov rule
        else :
          # grab relevant data from line1
          line1_list = line1.split( "_prov" )
          name1      = line1_list[0] + "_prov"
          remainder1 = line1_list[1]
          remainder1 = remainder1[16:]

          if DEBUG :
            print "line1      = " + str( line1 )
            print "name1      = " + str( name1 )
            print "remainder1 = " + str( remainder1 )
          
          # grab relevant data from line2
          if DEBUG :
            print "line2 = " + str( line2 )

          line2_list = line2.split( "_prov" )
          name2      = line2_list[0] + "_prov"
          remainder2 = line2_list[1]
          remainder2 = remainder2[16:]

          if DEBUG :      
            print "line2      = " + str( line2 )
            print "name2      = " + str( name2 )
            print "remainder2 = " + str( remainder2 )

          # identical names and remainders
          if (name1 == name2) and (remainder1 == remainder2) :
            noOccurence = False
            break
          

    # check if line1 appeared in file2
    if noOccurence : # line1 has no corresponding line in file2
      print "FATAL ERROR : '" + line1 + "' from file " + file1 + " has no corresponding line in file " + file2
      return False
    else :           # line1 has a corresponding line in file2
      pass


  # CASE : file2 contains a line not in file1
  for line2 in fileLines_2 :
    for line1 in fileLines_1 :
      pass

  return True


#########
#  EOF  #
#########
