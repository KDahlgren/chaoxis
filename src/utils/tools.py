#!/usr/bin/env python

'''
tools.py
   A storage location for generally applicable methods used to
   sanity-check particular properties.
'''

import inspect, os, random, re, string, sys, numbers

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

import dumpers
# ------------------------------------------------------ #

operators = [ "+", "-", "*", "/", "<", ">", "<=", ">=", "==" ]

#############
#  GLOBALS  #
#############
TOOLS_DEBUG = False


#####################
#  BREAKPOINT (bp)  #
#####################
def bp( filename, funcname, msg ) :
  sys.exit( "BREAKPOINT in file " + filename + " at function " + funcname + " :\n>>> " + msg )

############
#  GET ID  #
############
# input nothing
# output random 16 char alphanumeric id
def getID() :
  return "".join( random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(16) )

#########################
#  GET RANDOM ATT NAME  #
#########################
# input nothing
# output random 16 char alphanumeric id (all uppercase)
def getRandomAttName() :
  return "".join( random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16) )


##############################
#  GET EVAL RESULTS DICT C4  #
##############################
# get results from c4 output
# input results as an array
# output dictionary of results:
#     table names are keys, 
#     values are a list of rows split into lists on commas
#     { 'tableName' : [ ['a1', ..., 'aN'], ..., ['b1', ..., 'bN'] ] }
def getEvalResults_dict_c4( results_array ) :

  resultsDict = {}

  # ---------------------------------------------------------------------- #
  # CASE : results_array not empty                                         #
  # ---------------------------------------------------------------------- #
  if not results_array == [] :

    prevPrevLine = None
    prevLine     = None
    currLine     = None
    currRelation = None

    for i in range( 0, len( results_array ) ) :

      print " results_array[" + str(i) + "] = " + results_array[i]

      # get previous line
      if i > 0 :
        prevLine = results_array[ i-1 ]
      else :
        prevLine = None

      # get previous previous line
      if i > 1 :
        prevPrevLine = results_array[ i-2 ]
      else :
        prevPrevLine = None

      # get current line
      currLine     = results_array[ i ]

      # hit an empty relation
      if prevPrevLine == "---------------------------"  and currLine == "---------------------------"  :
        resultsDict[ currRelation ] = []

      # hit a delimiter line
      elif currLine == "---------------------------" :
        pass

      # hit a relation line
      elif prevLine == "---------------------------" :
        currRelation = currLine

      # hit a tuple line
      else :
        if currRelation in resultsDict :
          currList = resultsDict[ currRelation ]
        else :
          currList = []

        currList.append( currLine.split( ',' ) )
        resultsDict[ currRelation ] = currList

  # ---------------------------------------------------------------------- #
  # CASE: empty results array                                              #
  # ---------------------------------------------------------------------- #
  else :
    tools.bp( __name__, inspect.stack()[0][3], "No evaluation results." )

  return resultsDict


################################
#  CHECK IF REWRITTEN ALREADY  #
################################
def checkIfRewrittenAlready( rid, cursor ) :
  cursor.execute( "SELECT rewritten FROM Rule WHERE rid == '" + rid + "'" )
  flag = cursor.fetchone()

  #print "checkIfRewrittenAlready : rid = " + rid
  if flag == None :
    cursor.execute( "SELECT * FROM Rule WHERE rid=='" + rid + "'" )
    info = cursor.fetchall()
    info = toAscii_multiList( info )
    print "info = \n" + str(info)
    tools.bp( __name__, inspect.stack()[0][3], "flag is none" )

  #print "flag = " + str(flag)
  if flag[0] == "False" :
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
# check if a particular string corresponds to the name of a fact table.
def isFact( goalName, cursor ) :
    attIDsName = None
    cursor.execute( "SELECT attID,attName FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + str(goalName) + "'" )
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


######################
#  CHECK DATA TYPES  #
######################
# given a rule id, if the rule has one or more equations,
# make sure the data types of the variables in the equations are compatible.
# returns an array of relevant data
def checkDataTypes( rid, cursor ) :

  # initialization for clarity
  verificationResults = []
  verificationResults.append( None ) # boolean indicating data type comparability
  verificationResults.append( None ) # string of offensive eqn, None otherwise
  verificationResults.append( None ) # lhs data type in offensive eqn, None otherwise
  verificationResults.append( None ) # rhs data type of offensive eqn, None otherwise

  # first check if the rule has at least one eqn
  if containsEqn( rid, cursor ) :
    # get all eqn info (redundant, but only mildly suboptimal assuming small number of eqns per rule)
    cursor.execute( "SELECT eqn FROM Equation WHERE rid=='" + rid + "'" )
    allEqns = cursor.fetchall()
    allEqns = toAscii_list( allEqns )

    # for each eqn, get the variables
    for eqn in allEqns :
      varList = None
      for op in operators :
        if op in eqn :
          varList = eqn.split( op )
      if varList :
        print "varList = " + str(varList)
        # for each variable, get the types.
        typeList = []
        for var in varList :
          varType = getVarType( var, rid, cursor ) # 'string' or 'int'
          typeList.append( varType )

        #bp( __name__, inspect.stack()[0][3], "typeList = " + str(typeList) )

        flag    = True # glass half full =]
        lhsType = typeList[0] # assume equations will always be binary
        rhsType = typeList[1] # assume equations will always be binary
        for t1 in typeList :
          for t2 in typeList :
            if not t1 == t2 :
              flag = False # encountered a type mismatch

        # hit a type incompatibility
        if not flag :
          if not lhsType :
            bp( __name__, inspect.stack()[0][3], "hit a type incompatibility, but lhsType is None" )
          elif not rhsType :
            bp( __name__, inspect.stack()[0][3], "hit a type incompatibility, but rhsType is None" )
          else :
            verificationResults[0] = False
            verificationResults[1] = eqn
            verificationResults[2] = lhsType
            verificationResults[3] = rhsType

            return verificationResults

      else :
        bp( __name__, inspect.stack()[0][3], "FATAL ERROR: eqn " + eqn + " has no variables.\nAborting..." )


    # made it to here without returning, therefore, no type incompatibilities.
    verificationResults[0] = True

  # no equations => no danger of type incompatibility.
  else :
    verificationResults[0] = True

  return verificationResults


###############
#  IS STRING  #
###############
def isString( var ) :
  if "'" in var or '"' in var :
    return True
  else :
    return False


############
#  IS INT  #
############
def isInt( var ) :
  if var.isdigit() :
    return True
  else :
    return False


##################
#  GET VAR TYPE  #
##################
# look up the type from the goal or fact table (or clock schema, if subgoal name is 'clock')
def getVarType( var, rid, cursor ) :

  if isString( var ) :
    return "string"

  elif isInt( var ) :
    return "int"

  else :
    # get info for subgoal containing var
    cursor.execute( "SELECT subgoalName,attID,attName FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + rid + "' AND Subgoals.rid==SubgoalAtt.rid AND Subgoals.sid==SubgoalAtt.sid AND SubgoalAtt.attName=='" + var + "'" )
    info = cursor.fetchall()
    info = toAscii_multiList( info )

    if TOOLS_DEBUG :
      print "info = " + str(info)
  
    typeList = []
    for subgoal in info :
      subgoalName = subgoal[0]
      attID       = subgoal[1]
  
      if subgoalName == "clock" :
        if attID == 0 :
          typeList.append( "string" )
        elif attID == 1 :
          typeList.append( "string" )
        elif attID == 2 :
          typeList.append( "string" )
        elif attID == 3 :
          typeList.append( "string" )
        else :
          bp( __name__, inspect.stack()[0][3], "FATAL ERROR: clock only has schema arity 4, attempting to access index " + attID )
  
      elif isFact( subgoalName, cursor ) :
        cursor.execute( "SELECT attType FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + subgoalName + "' AND FactAtt.attID=='" + str(attID) + "'" )
        thisType = cursor.fetchone()
        thisType = toAscii_str( thisType )
        typeList.append( thisType )
  
      else : # it's a rule
        cursor.execute( "SELECT attType FROM Rule,GoalAtt WHERE Rule.rid==GoalAtt.rid AND Rule.goalName=='" + subgoalName + "' AND GoalAtt.attID=='" + attID + "'" )
        thisType = cursor.fetchone()
        thisType = toAscii_str( thisType )
        typeList.append( thisType )
  
    # make sure all types in type list agree
    for t1 in typeList :
      for t2 in typeList :
        if not t1 == t2 :
          bp( __name__, inspect.stack()[0][3], "FATAL ERROR : single variable has multiple type representations: " + str(typeList) + "\nAborting..." )
  
    return typeList[0]


##################
#  CONTAINS EQN  #
##################
# given a rule id, check if the rule has at least one equantion
def containsEqn( rid, cursor ) :
  # get all eqn info
  cursor.execute( "SELECT eqn FROM Equation WHERE rid=='" + rid + "'" )
  allEqns = cursor.fetchall()
  allEqns = toAscii_list( allEqns )

  if len( allEqns ) > 0 :
    return True
  else :
    return False


#########
#  EOF  #
######### 
