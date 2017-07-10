#!/usr/bin/env python

'''
tools.py
   A storage location for generally applicable methods used to
   sanity-check particular properties.
'''

import ConfigParser, inspect, os, random, re, string, sys, numbers

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../.." ) )

import dumpers
# ------------------------------------------------------ #

operators = [ "<", ">", "<=", ">=", "==",  "+", "-", "*", "/" ]

#############
#  GLOBALS  #
#############
TOOLS_DEBUG = False


#####################
#  BREAKPOINT (bp)  #
#####################
def bp( filename, funcname, msg ) :
  os.system( "rm IR.db" )
  sys.exit( "BREAKPOINT in file " + filename + " at function " + funcname + " :\n>>> " + msg )

################
#  GET CONFIG  #
################
def getConfig( section, option, dataType ) :

  # ---------------------------------------------- #
  # create config parser instance
  configs = ConfigParser.ConfigParser( )

  # ---------------------------------------------- #
  # read defaults first
  defaults_path = os.path.abspath( __file__ + "/.." ) + "/defaults.ini" # assume stored in src/utils/
  configs.read( defaults_path )

  # ---------------------------------------------- #
  # check if all debugs off
  debugs = configs.get( "GENERAL", "ALL_DEBUGS_OFF" ) # this is read as a str, not a bool
  if debugs == "True" :
    all_debug_off_path = os.path.abspath( __file__ + "/.." ) + "/all_debugs_off.ini" # assume stored in src/utils/
    configs.read( all_debug_off_path )

  # ---------------------------------------------- #
  # read user-specified settings, if applicable
  settings_path = os.path.abspath( os.getcwd() ) + "/settings.ini"
  if os.path.isfile( settings_path ) : # check if file exists first.
    configs.read( settings_path )

  # ---------------------------------------------- #
  # handle boolean configure types
  if dataType == bool :
    if configs.get(section, option) == "True"  :
      return True
    else :
      return False

  # ---------------------------------------------- #
  # handle list configure types
  elif dataType == list :

    if section == "CORE" and option == "CUSTOM_FAULT" :
      if configs.get(section, option) == "None" :
        return None

    list_str   = configs.get(section, option)
    list_str   = list_str.translate( None, string.whitespace )  # remove extra spaces and newlines
    list_str   = list_str[1:]                                   # remove leading open bracket
    list_str   = list_str[:-1]                                  # remove trailing close bracket
    list_array = list_str.split( "','" )                        # convert string to array
    clean_array = []
    for x in list_array :
      x = x.replace( "'", "" )                                  # remove straggling apostrophes
      clean_array.append( x )

    return clean_array

  # ---------------------------------------------- #
  # handle int configure types

  elif dataType == int :
    return int( configs.get( section, option ) )

  # ---------------------------------------------- #
  # otherwise treat as a string
  else :
    return configs.get(section, option)


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

########################
#  CLEAN FACT RECORDS  #
########################
def cleanFactRecords( factRecords_raw ) :

  pastIDs     = []
  factRecords = []  # list of lists of strings
  currRecord  = []  # list of strings

  for i in range(0, len(factRecords_raw)) :
    currRecord  = []
    currAtt     = factRecords_raw[i]
    currfid     = currAtt[0]
    currAttID   = currAtt[1]
    currAttName = currAtt[2]
    currTimeArg = currAtt[3]

    currAttName = currAttName.replace( "'", "" )
    currAttName = currAttName.replace( '"', '' )

    if not currfid in pastIDs :
      currRecord.append( currAttName )

      for j in range( i+1, len( factRecords_raw ) ) :
        nextAtt     = factRecords_raw[j]
        nextfid     = nextAtt[0]
        nextAttID   = nextAtt[1]
        nextAttName = nextAtt[2]
        nextTimeArg = nextAtt[3]

        nextAttName = nextAttName.replace( "'", "" )
        nextAttName = nextAttName.replace( '"', '' )

        if currfid == nextfid :
          currRecord.append( nextAttName )
        else :
          currRecord.append( currTimeArg )
          factRecords.append( currRecord )
          break

    pastIDs.append( currfid )

  return factRecords


##################
#  IS FACT NODE  #
##################
# check if the node should be a fact node
def isFactNode( goalName, triggerRecordList, cursor ) :

  cursor.execute( "SELECT Fact.fid,attID,attName,timeArg FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + str(goalName) + "'" )
  factRecords_raw = cursor.fetchall()
  factRecords_raw = toAscii_multiList( factRecords_raw )

  print "factRecords_raw :"
  for r in factRecords_raw :
    print r

  factRecords = cleanFactRecords( factRecords_raw )

  print
  print "factRecords :"
  for r in factRecords :
    print r

  # has to be a fact
  if goalName == "clock" :
    return True

  elif isFact( goalName, cursor ) :

    print "goalName = " + str( goalName )
    print "triggerRecordList = " + str( triggerRecordList )

    if triggerRecordList == [] :
      return True

    if type( triggerRecordList[0][1] ) is list :
      flag = True
      for trig in triggerRecordList :
        print "trig = " + str( trig )
        trigRecList = trig[2]
        print "trigRecList = " + str( trigRecList )
        for trigRec in trigRecList :
          if not trigRec in factRecords :
            return False

      if flag :
        return True
      else :
        return False

    else :
      for rec in triggerRecordList :
        if not rec in factRecords :
          print "RETURNING FALSE"
          return False
      print "RETURNING TRUE"
      return True # otherwise

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
          break
      if varList :
        #print "varList = " + str(varList)
        # for each variable, get the types.
        typeList = []
        for var in varList :
          varType = getVarType( var, rid, cursor ) # returns 'string' or 'int'
          typeList.append( varType )

        #bp( __name__, inspect.stack()[0][3], "typeList = " + str(typeList) )

        flag    = True         # glass half full =]
        lhsType = typeList[0]  # assume equations will always be binary
        rhsType = typeList[1]  # assume equations will always be binary
        for t1 in typeList :
          for t2 in typeList :
            if not t1 == t2 :
              flag = False     # encountered a type mismatch

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
  # clean var of operators
  for op in operators :
    if op in var :
      var = var.replace( op, "" )

  # check of positive integer
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

    #print "-----------------------"
    #print "info = " + str( info )

    # check if variable is defined in an equation
    if info == [] :
      cursor.execute( "SELECT rid,eid,eqn FROM Equation WHERE rid='" + rid + "'" )
      rule_eqns = cursor.fetchall()
      rule_eqns = toAscii_multiList( rule_eqns )
      eqns = [ eqn[2] for eqn in rule_eqns ]

      parsedEqns = []
      for eqn in eqns :
        #print "eqn = " + str( eqn )
        for op in operators :
          if op in eqn :
            #print eqn + " contains op " + op
            eqn_orig = eqn
            eqn = eqn.split( op )
            #print "split eqn = " + str( eqn )
            lhs = eqn[0]
            rhs = eqn[1]
            if lhs == var and isString( rhs ) :
              return "string"
            elif lhs == var and isInt( rhs ) :
              return "int"
            elif lhs == var :
              bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized type in eqn : " + str( eqn_orig ) )
            #else :
            #  print "could not match var " + var + " in eqn " + str( eqn )
      bp( __name__, inspect.stack()[0][3], "FATAL ERROR : variable " + var + " not defined in rule\n" + dumpers.reconstructRule( rid, cursor ) )

    # variable exists in subgoal
    else :
      typeList = []
      #print "info = " + str( info )
      for subgoal in info :
        subgoalName = subgoal[0]
        attID       = subgoal[1]
  
        if subgoalName == "clock" :
          if attID == 0 :
            typeList.append( "string" )
          elif attID == 1 :
            typeList.append( "string" )
          elif attID == 2 :
            #typeList.append( "string" )
            typeList.append( "int" )
          elif attID == 3 :
            #typeList.append( "string" )
            typeList.append( "int" )
          else :
            bp( __name__, inspect.stack()[0][3], "FATAL ERROR: clock only has schema arity 4, attempting to access index " + ( attID ) )
  
        elif isFact( subgoalName, cursor ) :
          cursor.execute( "SELECT attType FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + subgoalName + "' AND FactAtt.attID=='" + str( attID ) + "'" )
          thisType = cursor.fetchone()
          #print "IS FACT:"
          #print "subgoalName = " + subgoalName
          #print "thisType = " + str( thisType )
          thisType = toAscii_str( thisType )
          typeList.append( thisType )
  
        else : # it's a rule
          cursor.execute( "SELECT attType FROM Rule,GoalAtt WHERE Rule.rid==GoalAtt.rid AND Rule.goalName=='" + subgoalName + "' AND GoalAtt.attID=='" + str( attID ) + "'" )
          thisType = cursor.fetchone()
          #print "IS RULE:"
          #print "subgoalName = " + subgoalName
          #print "thisType = " + str( thisType )
          thisType = toAscii_str( thisType )
          typeList.append( thisType )
  
      # make sure all types in type list agree
      for t1 in typeList :
        for t2 in typeList :
          if not t1 == t2 :
            bp( __name__, inspect.stack()[0][3], "FATAL ERROR : single variable has multiple type representations: " + str(typeList) + "\nAborting..." )

    #print "var = " + str( var )
    #print "rid = " + rid
    #print dumpers.reconstructRule( rid, cursor )
    #print "typeList = " + str( typeList ) 
    #print "-----------------------"
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
