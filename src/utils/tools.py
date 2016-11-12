#!/usr/bin/env python

'''
tools.py
   A storage location for generally applicable methods used to
   sanity-check particular properties.
'''

import os, random, string, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

#from utils import extractors
# ------------------------------------------------------ #

############
#  GET ID  #
############
# input nothing
# output random 16 char alphanumeric id
def getID() :
  return "".join( random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16) )


#######################
#  CHECK PARENTHESES  #
#######################
def checkParentheses( line ) :
  numOpen   = 0 # number of open parentheses "("
  numClosed = 0 # number of closed parentheses ")"

  for c in line :
    if c == "(" :
      numOpen += 1
    elif c == ")" :
      numClosed += 1

  if not numOpen == numClosed :
    sys.exit( "ERROR: Incorrect number of parentheses in line: " + line )

  return True


###################
#  TO ASCII LIST  #
###################
# input list of unicoded sql results
# output list of ascii results
def toAscii_list( sqlresults ) :

  cleanResults = []
  for r in sqlresults :
    if not r[0] == None :
      asciiResult = r[0].encode('utf-8')
      cleanResults.append( asciiResult )

  if not cleanResults == None :
    return cleanResults
  else :
    return None

##################
#  TO ASCII STR  #
##################
# input one sql output string
# output ascii version
def toAscii_str( unicodeStr ) :
  return unicodeStr[0].encode( 'utf-8' )


##########
#  SKIP  #
##########
# input a ded line
# determine if line is a comment
# output boolean
def skip( line ) :
  line = line.translate( None, string.whitespace )
  
  if (not line == None) and (len(line) > 0) : # skip blank lines
    if (not line[0] == "/") and (not line[1] == "/") :
      return False

  return True


############################
#  GET ALL INCLUDED FILES  #
############################
# input a dictionary of file names and examinations statuses
# output a complete list of files associated with a particular Dedalus program

def getAllIncludedFiles( fileDict ) :

  # base case
  noMoreNewFiles = True
  for k,v in fileDict.items() :
    if v == False :
      noMoreNewFiles = False

  # unexplored files exist
  if not noMoreNewFiles :
    print "fileDict1 = " + str( fileDict )

    # iterate over all files
    for filename, status in fileDict.items() :

      # hit an unexplored file
      if status == False :

        # check if file exists
        filepath = os.path.abspath( filename )
        if os.path.isfile( filepath ) :
          infile = open( filename, 'r' )

          # iterate over all lines in input file
          for line in infile :
            if not skip( line ) :
              if "include" in line :
                line    = line.split( " " )
                newfile = line[1].translate( None, string.whitespace )
                fileDict[ newfile ] = False
          infile.close()
          fileDict[ filename ] = True

        else :
          sys.exit( "ERROR : file does not exist: " + str(filename) )

    print "fileDict2 = " + str( fileDict )
    fileDict = getAllIncludedFiles( fileDict )

  return fileDict


###################
#  COMBINE LINES  #
###################
# input list of c4-formatted table definitions, facts, and rules
# output a single line containing the entire program

def combineLines( definesList, factsList, rulesList ) :
  program = ""

  # get defines
  for d in definesList :
    program += d

  # get facts
  for f in factsList :
    program += f

  # get rules
  for r in rulesList :
    program += r

  return program

#########
#  EOF  #
######### 
