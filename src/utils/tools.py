#!/usr/bin/env python

'''
tools.py
   A storage location for generally applicable methods used to
   sanity-check particular properties.
'''

import os, random, re, string, sys, numbers

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

import dumpers
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
TOOLS_DEBUG = False


############
#  GET ID  #
############
# input nothing
# output random 16 char alphanumeric id
def getID() :
  return "".join( random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(16) )


#########################
#  GET EVAL RESULTS C4  #
#########################
# get results from c4 output file
# input path to c4 results file
# output clean dictionary of results:
#     table names are keys, 
#     values are a list of rows split into lists on commas
#     { 'tableName' : [ ['a1', ..., 'aN'], ..., ['b1', ..., 'bN'] ] }
def getEvalResults_file_c4( path ) :

  if os.path.exists( path ) :
    fo = open( path )

    prevLine = None
    currRel  = None

    resultsDict = {}
    save        = False
    tupleList   = []

    for line in fo :

      if line == "\n" :
        resultsDict[ currRel ] = tupleList
        currRel = None
        tupleList = []
        save = False

      elif prevLine == "---------------------------" :
        currRel = line.rstrip()
        save    = True

      elif save == True :
        tupleList.append( line.rstrip() )


      prevLine = line.rstrip()

    fo.close()

  else :
    sys.exit( "Cannot open file : " + path )

  if TOOLS_DEBUG :
    print "resultsDict : "
    for key in resultsDict :
      print "key = " + str(key) + " : "
      print resultsDict[ key ]

  cleanResultsDict = {}
  for key in resultsDict :
    tupList = []
    for tup in resultsDict[ key ] :
      tup = tup.split( "," )
      tupList.append( tup )
    cleanResultsDict[ key ] = tupList

  if TOOLS_DEBUG :
    print "cleanResultsDict : "
    for key in cleanResultsDict :
      print "key = " + str(key) + " : "
      print cleanResultsDict[ key ]

  return cleanResultsDict


################################
#  CHECK IF REWRITTEN ALREADY  #
################################
def checkIfRewrittenAlready( rid, cursor ) :
  cursor.execute( "SELECT rewritten FROM Rule WHERE rid == '" + rid + "'" )
  flag = cursor.fetchone()
  flag = flag[0]
  if flag == 0 :
    return False
  else :
    if TOOLS_DEBUG :
      print "RULE PREVIOUSLY REWRITTEN: " + str( dumpers.reconstructRule( rid, cursor ) )
    return True


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
# input list of unicoded sql results (array of unary tuples)
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

#########################
#  TO ASCII MULTI LIST  #
#########################
# input list of unicoded sql results (n-ary tuples)
# output list of ascii results as an array of n-ary arrays
def toAscii_multiList( tupleList ) :

  cleanResults = []

  for tup in tupleList :
    if TOOLS_DEBUG :
      print "TOOLS tup = " + str(tup)
    cleanTup = []
    for item in tup :
      if TOOLS_DEBUG :
        print "TOOLS tup item  = "
        print item
      if isinstance(item, numbers.Real) :
        cleanTup.append( item )
      else :
        # cleanse the unicode
        #if not item[0] == None :
        #  asciiResult = item[0].encode('utf-8')
        #  cleanTup.append( asciiResult )
        if not item == None :
          asciiResult = item.encode('utf-8')
          cleanTup.append( asciiResult )
    cleanResults.append( cleanTup )

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
    if TOOLS_DEBUG :
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
                newfile = line[1]
                newfile = newfile.replace( ";", "" )
                newfile = newfile.replace( '"', "" )
                newfile = newfile.replace( "'", "" )
                newfile  = newfile.translate( None, string.whitespace ) # removes extra spaces and newlines
                fileDict[ newfile ] = False
          infile.close()
          fileDict[ filename ] = True

        else :
          sys.exit( "ERROR : file does not exist: " + str(filename) )

    if TOOLS_DEBUG :
      print "fileDict2 = " + str( fileDict )
    fileDict = getAllIncludedFiles( fileDict )

  return fileDict


###################
#  COMBINE LINES  #
###################
# input list of c4-formatted table definitions, facts, and rules
# output a single line containing the entire program

def combineLines( listOfStatementLists ) :
  program = ""

  for listOfStatments in listOfStatementLists :
    for statement in listOfStatments :
      program += statement

  return program


######################
#  ATT SEARCH PASS 2 #
######################
# input list of any formatted datalog rule, possibly containing wild cards
#    of the form 'THISISAWILDCARD<16 random upper-case letters>'
# output an array containing the extracted wildcards

def attSearchPass2( pydatalogRule ) :
  wildList = []

  pydatalogRule = pydatalogRule.split(",")

  # iterate over components of the rule to extract all wildcards
  for substr in pydatalogRule :
    if TOOLS_DEBUG :
      print " >>> substr = " + substr
    r = re.search('THISISAWILDCARD([A-Z]*)', substr)
    if r :
      r = r.group(0)
      if TOOLS_DEBUG :
        print ">>>> r = " + str(r)
      wildList.append(r)

  return wildList

#############
#  IS FACT  #
#############
def isFact( goalName, cursor ) :
    attIDsName = None
    cursor.execute( "SELECT attID,attName FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name == '" + str(goalName) + "'" )
    attIDsNames = cursor.fetchall()
    attIDsNames = toAscii_multiList( attIDsNames )

    if TOOLS_DEBUG :
      print "in RuleNode isFact:"
      print "name        = " + name
      print "attIDsNames = " + str(attIDsNames)

    if attIDsNames or (goalName == "clock") :
      return True
    else :
      return False

#########
#  EOF  #
######### 
